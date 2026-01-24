export default function Footer() {
  return (
    <footer className="border-t border-surface-hover mt-20">
      <div className="max-w-5xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
        <p className="text-muted text-sm font-heading tracking-wider uppercase">
          amoredatus / lovedata
        </p>
        <p className="text-muted text-sm">
          &copy; {new Date().getFullYear()} amoredatus. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
