import { getDictionary } from '../dictionaries/get-dictionary'
import { Locale } from '../i18n-config'
import HomeClient from '../components/HomeClient'

type Props = {
  params: Promise<{ lang: Locale }>
};

export default async function Home({ params }: Props) {
  const { lang } = await params;
  const dict = await getDictionary(lang);
  return <HomeClient dict={dict} />;
}