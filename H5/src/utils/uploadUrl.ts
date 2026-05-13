export function getUploadUrl(url: string | null | undefined): string {
  if (!url) return ''
  if (url.startsWith('blob:') || url.startsWith('data:') || url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  const token = localStorage.getItem('h5_token') || localStorage.getItem('token')
  const separator = url.includes('?') ? '&' : '?'
  return token ? `${url}${separator}token=${encodeURIComponent(token)}` : url
}
