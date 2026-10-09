// Minimal stand-in for the TinyMCE editor: shows the content as rich text.
export function Editor(props: any) {
  return <div className="min-h-[120px] rounded border border-slate-200 bg-white p-3 text-sm" dangerouslySetInnerHTML={{ __html: props.value ?? props.initialValue ?? '' }} />;
}
