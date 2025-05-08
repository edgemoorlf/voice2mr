"use client";

import { useState } from 'react'
import FileUploader from '@/components/FileUploader'
import { createMedicalRecord } from '@/lib/api'

export default function Home() {
  const [transcript, setTranscript] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      const result = await createMedicalRecord(files, transcript)
      setSuccessMessage('Medical record created successfully!')
      setTranscript('')
      setFiles([])
    } catch (error) {
      console.error('Submission failed:', error)
      alert('Failed to create medical record')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6">New Medical Record</h1>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">
            Clinical Notes
          </label>
          <textarea
            className="w-full p-3 border rounded-lg"
            rows={4}
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Enter clinical notes or paste transcript..."
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">
            Attach Files (Audio/Images/Text)
          </label>
          <FileUploader
            onUploadStart={() => setUploading(true)}
            onUploadSuccess={(uploadedFiles: File[]) => {
              setUploading(false);
              // Handle successful upload response
              console.log('Upload successful:', uploadedFiles);
              setFiles(prev => [...prev, ...uploadedFiles]);
            }}
            onUploadError={(error) => {
              setUploading(false);
              console.error('Upload error:', error);
              alert(`Upload failed: ${error.message}`);
            }}
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {isSubmitting ? 'Processing...' : 'Create Record'}
        </button>
      </form>

      {successMessage && (
        <div className="mt-4 p-4 bg-green-100 text-green-800 rounded-lg">
          {successMessage}
        </div>
      )}
    </div>
  )
}
