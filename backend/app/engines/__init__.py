"""
Chunking engine for large dataset processing
"""
import pandas as pd
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import json


class ChunkingEngine:
    """Handles splitting large CSV files into manageable chunks"""
    
    DEFAULT_CHUNK_SIZE = 10000  # rows per chunk
    DEFAULT_CHUNK_DIR = "/tmp/transactiq_chunks"
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_dir: str = DEFAULT_CHUNK_DIR):
        self.chunk_size = chunk_size
        self.chunk_dir = chunk_dir
        self.chunks: List[Dict[str, Any]] = []
        
        # Create chunk directory if it doesn't exist
        Path(self.chunk_dir).mkdir(parents=True, exist_ok=True)
    
    def split_dataset(self, df: pd.DataFrame, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Split large dataset into chunks
        
        Returns list of chunk metadata
        """
        self.chunks = []
        total_rows = len(df)
        chunk_count = (total_rows + self.chunk_size - 1) // self.chunk_size
        
        for chunk_num in range(chunk_count):
            start_idx = chunk_num * self.chunk_size
            end_idx = min((chunk_num + 1) * self.chunk_size, total_rows)
            
            chunk_df = df.iloc[start_idx:end_idx]
            chunk_metadata = self._save_chunk(
                chunk_df,
                dataset_id,
                chunk_num,
                start_idx,
                end_idx
            )
            self.chunks.append(chunk_metadata)
        
        return self.chunks
    
    def _save_chunk(
        self,
        chunk_df: pd.DataFrame,
        dataset_id: str,
        chunk_number: int,
        start_row: int,
        end_row: int
    ) -> Dict[str, Any]:
        """Save chunk to disk and return metadata"""
        chunk_filename = f"{dataset_id}_chunk_{chunk_number:05d}.csv"
        chunk_path = os.path.join(self.chunk_dir, chunk_filename)
        
        # Save chunk
        chunk_df.to_csv(chunk_path, index=False)
        
        # Get file size
        file_size = os.path.getsize(chunk_path)
        
        # Create metadata
        metadata = {
            "id": f"{dataset_id}_{chunk_number:05d}",
            "dataset_id": dataset_id,
            "chunk_number": chunk_number,
            "start_row": start_row,
            "end_row": end_row,
            "record_count": len(chunk_df),
            "file_path": chunk_path,
            "file_size_bytes": file_size,
            "is_processed": False,
            "error_count": 0,
            "warning_count": 0
        }
        
        return metadata
    
    def get_chunk(self, chunk_id: str) -> Optional[pd.DataFrame]:
        """Load chunk from disk"""
        chunk = next((c for c in self.chunks if c["id"] == chunk_id), None)
        if not chunk:
            return None
        
        try:
            return pd.read_csv(chunk["file_path"])
        except Exception as e:
            print(f"Error loading chunk {chunk_id}: {e}")
            return None
    
    def merge_chunks(self, dataset_id: str) -> pd.DataFrame:
        """Merge all chunks back into single dataframe"""
        chunk_dfs = []
        
        for chunk_meta in self.chunks:
            df = pd.read_csv(chunk_meta["file_path"])
            chunk_dfs.append(df)
        
        if not chunk_dfs:
            return pd.DataFrame()
        
        return pd.concat(chunk_dfs, ignore_index=True)
    
    def clean_chunks(self, dataset_id: str):
        """Delete chunk files for dataset"""
        for chunk_meta in self.chunks:
            try:
                if os.path.exists(chunk_meta["file_path"]):
                    os.remove(chunk_meta["file_path"])
            except Exception as e:
                print(f"Error deleting chunk {chunk_meta['id']}: {e}")
        
        self.chunks = []
    
    def get_chunk_statistics(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for specific chunk"""
        chunk = next((c for c in self.chunks if c["id"] == chunk_id), None)
        if not chunk:
            return None
        
        df = self.get_chunk(chunk_id)
        if df is None:
            return None
        
        stats = {
            "chunk_id": chunk_id,
            "record_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "file_size_bytes": chunk["file_size_bytes"],
            "missing_values": df.isnull().sum().to_dict(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return stats
