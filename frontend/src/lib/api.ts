import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface MedicalRecord {
  id: string
  content: string
  files: string[]
  created_at: string
}

export const createMedicalRecord = async (files: File[], transcript: string) => {
  const formData = new FormData()
  
  // Append files with backend-compatible structure
  files.forEach((file, index) => {
    formData.append(`files`, file)
    formData.append(`content_types`, file.type)
  })
  
  formData.append('medical_records', transcript)
  formData.append('is_json', 'true')

  const response = await apiClient.post('/v2mr', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const getMedicalRecords = async () => {
  const response = await apiClient.get<MedicalRecord[]>('/medical-records')
  return response.data
}

export const sendMessage = async (message: string) => {
  try {
    const response = await apiClient.post('/query', {
      prompt: message,
      role: 'patient',
    });
    return response.data;
  } catch (error) {
    console.error(error);
  }
}