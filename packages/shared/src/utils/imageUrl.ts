export function getFullImageUrl(url: string): string {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url
  }
  let fullUrl = window.location.origin + url
  const token = localStorage.getItem('token')
  if (token) {
    const separator = fullUrl.includes('?') ? '&' : '?'
    fullUrl += `${separator}token=${encodeURIComponent(token)}`
  }
  return fullUrl
}
