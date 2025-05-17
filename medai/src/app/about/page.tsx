import type { Dictionary } from '@/types/dictionary';

export default function About({ dict }: { dict: Dictionary }) {
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">{dict.about.title}</h1>
        
        <div className="prose max-w-none">
          <p className="text-lg text-gray-600 mb-6">
            {dict.about.description}
          </p>

          <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">{dict.about.mission.title}</h2>
          <p className="text-gray-600 mb-6">
            {dict.about.mission.content}
          </p>

          <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">{dict.about.howItWorks.title}</h2>
          <ul className="list-disc pl-6 text-gray-600 mb-6">
            {dict.about.howItWorks.items.map((item, index) => (
              <li key={index} className="mb-2">{item}</li>
            ))}
          </ul>

          <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">{dict.about.notice.title}</h2>
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
            <p className="text-yellow-700">
              {dict.about.notice.content}
            </p>
          </div>

          <h2 className="text-xl font-semibold text-gray-900 mt-8 mb-4">{dict.about.privacy.title}</h2>
          <p className="text-gray-600 mb-6">
            {dict.about.privacy.content}
          </p>
        </div>
      </div>
    </div>
  );
} 