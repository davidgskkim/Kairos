import React, { useState, useCallback } from 'react';
import { UploadCloud, Loader2 } from 'lucide-react';

interface FileDropzoneProps {
  onFileUpload: (file: File) => void;
  loading: boolean;
}

export function FileDropzone({ onFileUpload, loading }: FileDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileUpload(e.dataTransfer.files[0]);
    }
  }, [onFileUpload]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div
      className={`relative group border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ease-in-out cursor-pointer
        ${isDragging 
          ? "border-blue-400 bg-blue-500/10 scale-[1.02]" 
          : "border-slate-700 hover:border-slate-500 hover:bg-slate-800/50"
        }
      `}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept=".xlsx"
        onChange={handleChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={loading}
      />

      <div className="flex flex-col items-center justify-center gap-3">
        {loading ? (
          <Loader2 className="w-10 h-10 text-blue-400 animate-spin" />
        ) : (
          <div className={`p-3 rounded-full transition-colors ${isDragging ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-800 text-slate-400 group-hover:text-slate-200'}`}>
            <UploadCloud className="w-8 h-8" />
          </div>
        )}
        
        <div className="space-y-1">
          <p className="text-sm font-medium text-slate-200">
            {loading ? "Processing..." : "Click or drag availability sheet"}
          </p>
          <p className="text-xs text-slate-500">
            Supports .xlsx files only
          </p>
        </div>
      </div>
    </div>
  );
}