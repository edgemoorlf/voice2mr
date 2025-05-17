export type Dictionary = {
  appTitle: string
  appSubtitle: string
  uploadMedicalRecords: string
  upload: {
    description: string
    dragDropText: string
    supportedFormats: string
  }
  chat: {
    welcomeMessage: string
    inputPlaceholder: string
    recordingStarted: string
    recordingStopped: string
    microphoneError: string
    processingError: string
    voiceInputError: string
  }
  about: {
    title: string
    description: string
    mission: {
      title: string
      content: string
    }
    howItWorks: {
      title: string
      items: string[]
    }
    notice: {
      title: string
      content: string
    }
    privacy: {
      title: string
      content: string
    }
  }
} 