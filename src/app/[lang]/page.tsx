import { getDictionary } from '../dictionaries/get-dictionary'
import { Locale } from '../i18n-config'
import HomeClient from '../components/HomeClient'

type Props = {
  params: Promise<{ lang: Locale }>; // params is a Promise
};

export default async function Home({ params: paramsPromise }: Props) { // Renamed for clarity
  const resolvedParams = await paramsPromise; // Await the promise
  const lang = resolvedParams.lang;       // Access lang from the resolved object

  const dict = await getDictionary(lang);
  
  return <HomeClient dict={dict} />;
}