"use client";

import { useState, useCallback } from 'react'
import { UploadCloud, Mic, Image, Text, X, Loader } from 'lucide-react'

interface FileUploaderProps {
  onUploadStart: () => void
  onUploadSuccess: (uploadedFiles: File[]) => void
  onUploadError: (error: Error) => void
}

interface FileWithPreview {
  file: File;
  preview?: string;
  type: string;
  status: 'pending' | 'uploading' | 'done' | 'error';
  name: string;
  size: number;
}

export default function FileUploader({ onUploadStart, onUploadSuccess, onUploadError }: FileUploaderProps) {
  const [files, setFiles] = useState<FileWithPreview[]>([])
  const MAX_FILE_SIZE_MB = 100

  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return
    
    const newFiles = Array.from(e.target.files).map(file => {
      // Preserve the original File instance
      const fileObj = new File([file], file.name, { type: file.type });
      return {
        file: fileObj,  // Store original File instance
        preview: file.type?.startsWith('image/') ? URL.createObjectURL(fileObj) : undefined,
        type: fileObj.type || 'application/octet-stream',
        status: 'pending' as const,
        name: fileObj.name,
        size: fileObj.size
      }
    })

    // Validate files
    const validFiles = newFiles.filter(file => {
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        onUploadError(new Error(`File ${file.name} exceeds ${MAX_FILE_SIZE_MB}MB limit`))
        return false
      }
      return true
    })

    setFiles(prev => [...prev, ...validFiles])
    onUploadStart()
    
    try {
      setFiles(prev => prev.map(f => 
        validFiles.some(vf => vf.name === f.name) ? {...f, status: 'uploading'} : f
      ))

      const formData = new FormData()
      validFiles.forEach(({ file }) => formData.append('files', file))
      // Match backend API parameters exactly
      formData.append('medical_records', '')  // Required empty string parameter
      formData.append('is_json', 'true')      // FastAPI requires lowercase 'true'/'false' strings

      const response = await fetch('http://192.168.20.84:8000/v2mr', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          'X-Client-Type': 'web-portal'
        },
      })

      if (!response.ok) throw new Error('Upload failed')

      setFiles(prev => prev.map(f => 
        validFiles.some(vf => vf.name === f.name) ? {...f, status: 'done'} : f
      ))
      onUploadSuccess(validFiles.map(f => f.file))
    } catch (error) {
      setFiles(prev => prev.map(f => 
        validFiles.some(vf => vf.name === f.name) ? {...f, status: 'error'} : f
      ))
      onUploadError(error instanceof Error ? error : new Error('Upload failed'))
    }
  }, [onUploadStart, onUploadSuccess, onUploadError])

  const removeFile = (fileName: string) => {
    setFiles(prev => prev.filter(f => f.name !== fileName))
  }

  return (
    <div className="p-4 border-2 border-dashed border-gray-300 rounded-lg w-full max-w-2xl">
      <div className="flex flex-col items-center gap-4">
        <UploadCloud className="w-8 h-8 text-gray-500" />
        <div className="flex flex-col gap-4 w-full">
          {/* File previews */}
          {files.map((file) => (
            <div key={`${file.name}-${file.size}-${file.file.lastModified}`} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2">
                {file.preview ? (
                  <img
                    src={file.preview}
                    alt={file.name}
                    className="w-8 h-8 object-cover rounded"
                    onLoad={() => URL.revokeObjectURL(file.preview!)}
                  />
                ) : (
                  <div className="w-8 h-8 flex items-center justify-center bg-gray-200 rounded">
                    {(file.type?.startsWith('audio/') || file.type?.startsWith('video/')) ? (
                      <Mic className="w-4 h-4 text-gray-600" />
                    ) : (
                      <Text className="w-4 h-4 text-gray-600" />
                    )}
                  </div>
                )}
                <div>
                  <p className="text-sm font-medium">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)}MB
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {file.status === 'uploading' && <Loader className="w-4 h-4 animate-spin" />}
                {file.status === 'done' && (
                  <span className="text-green-500">✓</span>
                )}
                {file.status === 'error' && (
                  <span className="text-red-500">✕</span>
                )}
                <button
                  type="button"
                  onClick={() => removeFile(file.name)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
          <label className="flex items-center gap-1 px-4 py-2 bg-blue-100 text-blue-800 rounded-full cursor-pointer">
            <Mic className="w-4 h-4" />
            Audio
            <input
              type="file"
              accept="audio/*,video/quicktime,audio/quicktime,.mov,video/mp4,.mp4,audio/mpeg,audio/wav,audio/ogg,audio/webm,audio/aac,audio/x-m4a"
              multiple
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
          <label className="flex items-center gap-1 px-4 py-2 bg-green-100 text-green-800 rounded-full cursor-pointer">
            <Image className="w-4 h-4" />
            Images
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
          <label className="flex items-center gap-1 px-4 py-2 bg-purple-100 text-purple-800 rounded-full cursor-pointer">
            <Text className="w-4 h-4" />
            Text
            <input
              type="file"
              accept=".txt,.md"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
        </div>
      </div>
    </div>
  )
}
