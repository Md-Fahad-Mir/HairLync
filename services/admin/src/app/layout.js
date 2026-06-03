export const metadata = {
  title: 'HairIQ — Admin Dashboard',
  description: 'Control and monitor HairIQ AI and user accounts.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'system-ui, sans-serif', backgroundColor: '#0d1117', color: '#c9d1d9' }}>
        {children}
      </body>
    </html>
  );
}
