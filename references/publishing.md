# Publishing

Use this reference when preparing H5/HTML distribution.

## Recommended Pattern

For long reports, use:

```text
Public-account article / email / message
  -> short guide and QR code
  -> H5 full report
  -> optional download link
```

Do not rely on copying a complex H5 page directly into a public-account editor. Many editors sanitize scripts and CSS.

## Download

For reliable direct download, host the downloadable file on an HTTPS server or object storage bucket and set:

```http
Content-Type: text/html; charset=utf-8
Content-Disposition: attachment; filename="industry-digest.html"
```

For static hosts that cannot set headers, provide a fallback instruction:

```text
If the in-app browser cannot download the file, open this page in the system browser and try again.
```

## QR Code

The QR code should point to the H5 reading page, not directly to a file download, unless the user explicitly wants a download-only workflow.

## WeChat

A common pattern is:

- article body: guide, highlights, QR code;
- "read more" / original link: H5 page;
- H5 page: full report and download buttons.
