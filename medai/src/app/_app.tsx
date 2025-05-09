import { AppProps } from 'next/app';
import { appWithTranslation } from 'next-i18next';
import '../styles/globals.css'; // Assuming you have a global CSS file

function MyApp({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}

export default appWithTranslation(MyApp); 