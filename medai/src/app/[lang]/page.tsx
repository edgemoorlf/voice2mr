import { getDictionary } from '../dictionaries/get-dictionary'
import { Locale } from '../i18n-config'
import HomeClient from '../components/HomeClient'

type Props = {
  params: Promise<{ lang: Locale }>; // params is a Promise
};

export default async function Home({ params }: Props) {
  const { lang } = await params;
  console.log('Loading dictionary for language:', lang);
  const dict = await getDictionary(lang);
  console.log('Loaded dictionary:', dict);
  
  return <HomeClient dict={dict} />;
}