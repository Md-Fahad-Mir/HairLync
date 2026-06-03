export const metadata = {
  title: 'HairIQ — Premium Hair Analysis & Recommendations',
  description: 'Unlock your hair potential with premium AI hair analysis and styling recommendations.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'system-ui, sans-serif', backgroundColor: '#0b0c10', color: '#c5c6c7' }}>
        {children}
      </body>
    </html>
  );
}
