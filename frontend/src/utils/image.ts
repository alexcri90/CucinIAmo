// ═══════════════════════════════════════════════════════════════
// 📸 IMAGE UTILS - Compressione client-side per l'analisi AI
//
// La foto NON viene mai salvata (Cloud Storage non è nel piano
// gratuito): viene solo compressa e inviata a Gemini per la stima.
// Ridurre a ~1024px/JPEG 0.8 taglia latenza e consumo di quota.
// ═══════════════════════════════════════════════════════════════

const MAX_SIDE = 1024;
const JPEG_QUALITY = 0.8;

export interface CompressedImage {
  /** Base64 puro (senza prefisso data:), pronto per inlineData di Gemini. */
  base64: string;
  mimeType: 'image/jpeg';
  /** Data URL per l'anteprima nella UI. */
  dataUrl: string;
}

function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('Immagine non leggibile. Prova con un altro file.'));
    img.src = url;
  });
}

/** Ridimensiona e comprime una foto (lato lungo ≤1024px, JPEG). */
export async function compressImage(file: File): Promise<CompressedImage> {
  const objectUrl = URL.createObjectURL(file);
  try {
    const img = await loadImage(objectUrl);
    const scale = Math.min(1, MAX_SIDE / Math.max(img.naturalWidth, img.naturalHeight));
    const width = Math.max(1, Math.round(img.naturalWidth * scale));
    const height = Math.max(1, Math.round(img.naturalHeight * scale));

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Canvas non disponibile in questo browser.');
    ctx.drawImage(img, 0, 0, width, height);

    const dataUrl = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
    const base64 = dataUrl.split(',')[1];
    if (!base64) throw new Error('Compressione della foto fallita.');

    return { base64, mimeType: 'image/jpeg', dataUrl };
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}
