import type { Dictionary } from '@/types/dictionary';
import { getDictionary } from '../dictionaries/get-dictionary';
import type { Locale } from '../../i18n-config';
import { logPageAccess } from '@/utils/pageLogger';

// Force dynamic rendering for logging
export const dynamic = 'force-dynamic';

// EXTREME DIAGNOSTIC ATTEMPT: Typing params AND searchParams as Promises.
// This is NOT standard for App Router and is for diagnosis only.
export default async function About(props: {
  params: Promise<{ lang: Locale }>; 
  searchParams?: Promise<{ [key: string]: string | string[] | undefined }>; // Treating searchParams as a Promise
}) {
  const { lang } = await props.params;
  
  // Log page access
  await logPageAccess(`/${lang}/about`, {
    language: lang,
    page: 'about'
  });
  
  // const actualSearchParams = props.searchParams ? await props.searchParams : undefined; // How you might access it
  const dict = await getDictionary(lang) as Dictionary;

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