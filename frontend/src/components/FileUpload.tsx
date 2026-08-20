'use client'

import { useState } from 'react'
import { Upload, FileText, Loader2 } from 'lucide-react'

interface FileUploadProps {
  title: string
  source: string
  acceptedFormats: string
  onUpload: (source: string, file: File) => void
  isLoading: boolean
}

export default function FileUpload({
  title,
  source,
  acceptedFormats,
  onUpload,
  isLoading
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(source, selectedFile)
      setSelectedFile(null)
    }
  }

  const getSourceIcon = () => {
    switch (source) {
      case 'account': return '🏦'
      case 'wallet': return '👛'
      case 'card': return '💳'
      default: return '📄'
    }
  }

  return (
    <div
      className={`bg-white rounded-lg border-2 border-dashed p-6 transition-all ${
        isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="flex flex-col items-center">
        <span className="text-3xl mb-2">{getSourceIcon()}</span>
        <h3 className="font-medium text-gray-900 mb-1">{title}</h3>
        <p className="text-xs text-gray-500 mb-4">{acceptedFormats}</p>
        
        {selectedFile ? (
          <div className="w-full">
            <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3 mb-3">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-gray-500" />
                <span className="text-sm text-gray-700 truncate max-w-[150px]">
                  {selectedFile.name}
                </span>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <button
              onClick={handleUpload}
              disabled={isLoading}
              className="w-full bg-blue-600 text-white rounded-lg py-2 px-4 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Upload</span>
                </>
              )}
            </button>
          </div>
        ) : (
          <label className="w-full cursor-pointer">
            <div className="border-2 border-gray-300 border-dashed rounded-lg py-6 px-4 hover:border-blue-400 hover:bg-gray-50 transition-all">
              <div className="flex flex-col items-center">
                <Upload className="w-8 h-8 text-gray-400 mb-2" />
                <p className="text-sm text-gray-600">
                  Drag & drop or <span className="text-blue-600">browse</span>
                </p>
              </div>
            </div>
            <input
              type="file"
              accept={acceptedFormats}
              onChange={handleFileSelect}
              className="hidden"
            />
          </label>
        )}
      </div>
    </div>
  )
}
