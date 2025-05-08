export default function About() {
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">About MedAI</h1>
        
        <div className="prose max-w-none">
          <p className="text-lg text-gray-600 mb-6">
            MedAI is a free medical AI assistant designed to make healthcare more accessible to everyone,
            especially those in remote areas with limited access to medical services.
          </p>

          <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">Our Mission</h2>
          <p className="text-gray-600 mb-6">
            We believe that everyone deserves access to quality healthcare guidance. Our AI-powered
            platform helps bridge the gap by providing initial medical insights and recommendations
            based on your voice recordings, images, and previous medical records.
          </p>

          <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">How It Works</h2>
          <ul className="list-disc pl-6 text-gray-600 mb-6">
            <li className="mb-2">Upload voice recordings of your symptoms or medical concerns</li>
            <li className="mb-2">Share images of visible symptoms or previous medical records</li>
            <li className="mb-2">Receive AI-generated medical insights and recommendations</li>
            <li>Get your results in multiple languages (coming soon)</li>
          </ul>

          <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">Important Notice</h2>
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-yellow-700">
              MedAI is designed to provide initial guidance and should not replace professional medical advice.
              Always consult with a qualified healthcare provider for proper diagnosis and treatment.
            </p>
          </div>

          <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">Privacy & Security</h2>
          <p className="text-gray-600 mb-6">
            We take your privacy seriously. All uploaded files and medical information are processed
            securely and are not stored permanently on our servers. Our service adheres to strict
            medical data protection standards.
          </p>
        </div>
      </div>
    </div>
  );
} 