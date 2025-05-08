"use client";

import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { ArrowUpTrayIcon, ChatBubbleLeftIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import Chat from "@/components/Chat";

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [medicalRecord, setMedicalRecord] = useState("");

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      "audio/*": [".mp3", ".wav", ".m4a"],
      "video/*": [".mp4", ".mov"],
      "image/*": [".png", ".jpg", ".jpeg"]
    },
    onDrop: (acceptedFiles) => {
      setFiles([...files, ...acceptedFiles]);
    }
  });

  const handleSubmit = async () => {
    if (files.length === 0) {
      toast.error("Please upload at least one file");
      return;
    }

    setIsProcessing(true);
    const formData = new FormData();
    files.forEach(file => {
      formData.append("files", file);
    });

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://2cbd-210-12-23-178.ngrok-free.app';
      const response = await fetch(`${apiUrl}/a2mr`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to process files (server error).' }));
        throw new Error(errorData.detail || "Failed to process files");
      }

      const data = await response.json();
      setMedicalRecord(data.content);
      toast.success("Files processed successfully!");
    } catch (error) {
      console.error("Error processing files:", error);
      if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error("Failed to process files. Please try again.");
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Your AI Medical Assistant
          </h2>
          <p className="mt-4 text-lg leading-8 text-gray-600">
            Speak or type your medical questions, and upload relevant records for more personalized assistance
          </p>
        </div>

        <div className="space-y-8">
          {/* Chat Interface - Primary Feature */}
          <div className="bg-white shadow-lg rounded-lg p-6">
            <Chat medicalRecord={medicalRecord} />
          </div>

          {/* Medical Records Section - Secondary Feature */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Medical Records</h3>
            <p className="text-sm text-gray-600 mb-4">
              Optional: Upload medical records, images, or voice recordings for more context-aware assistance
            </p>
            
            <div 
              {...getRootProps()} 
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer"
            >
              <input {...getInputProps()} />
              <ArrowUpTrayIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600">
                Drag & drop files here, or click to select
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Supports audio (MP3, WAV), video (MP4), and images (PNG, JPG)
              </p>
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-900">Uploaded files:</h4>
                <ul className="mt-2 divide-y divide-gray-200 border-t border-b border-gray-200">
                  {files.map((file, index) => (
                    <li key={index} className="flex items-center justify-between py-2">
                      <span className="text-sm text-gray-500">{file.name}</span>
                      <button
                        onClick={() => setFiles(files.filter((_, i) => i !== index))}
                        className="text-sm text-red-600 hover:text-red-800"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>

                {/* Process Button */}
                <div className="mt-4">
                  <button
                    onClick={handleSubmit}
                    disabled={isProcessing || files.length === 0}
                    className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? (
                      <span>Processing...</span>
                    ) : (
                      <>
                        <ChatBubbleLeftIcon className="h-5 w-5 mr-2" />
                        Process Files
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Medical Record Display */}
            {medicalRecord && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Processed Medical Record:</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700">
                    {medicalRecord}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
