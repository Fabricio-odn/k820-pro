"""Converte imagens e GIFs para o formato da tela (128x128, RGB565). Precisa do Pillow."""
import os
import warnings

from . import protocolo as P

# Limites para não travar com arquivos enormes ou maliciosos (bomba de descompressão).
TAMANHO_MAX_ARQUIVO = 64 * 1024 * 1024
PIXELS_MAX = 40_000_000
QUADROS_MAX_LIDOS = 5000


def carregar(caminho, modo="cortar", fundo=(0, 0, 0)):
    """Devolve (quadros, tempos_ms) prontos para `protocolo.dados_tela`.

    modo "cortar" preenche a tela e corta as sobras; "encaixar" mostra a imagem
    inteira com faixas na cor `fundo`. GIFs com mais de 140 quadros são
    amostrados, somando os tempos dos quadros pulados para manter a duração.
    """
    try:
        from PIL import Image, ImageOps, ImageSequence
    except ImportError:
        raise RuntimeError("enviar imagens precisa do Pillow (dnf install python3-pillow)") from None

    if os.path.getsize(caminho) > TAMANHO_MAX_ARQUIVO:
        raise ValueError("arquivo grande demais (máximo 64 MB)")
    Image.MAX_IMAGE_PIXELS = PIXELS_MAX
    lado = P.TELA_LADO
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            img = Image.open(caminho)
        except (Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise ValueError("imagem grande demais") from None
        except (OSError, SyntaxError) as e:
            raise ValueError(f"não consegui abrir a imagem: {e}") from None
    with img:
        if img.width * img.height > PIXELS_MAX:
            raise ValueError("imagem grande demais")
        quadros, tempos = [], []
        for n, q in enumerate(ImageSequence.Iterator(img)):
            if n >= QUADROS_MAX_LIDOS:
                break
            rgb = q.convert("RGBA")
            base = Image.new("RGBA", rgb.size, fundo + (255,))
            rgb = Image.alpha_composite(base, rgb).convert("RGB")
            if modo == "cortar":
                rgb = ImageOps.fit(rgb, (lado, lado), Image.Resampling.LANCZOS)
            else:
                rgb = ImageOps.pad(rgb, (lado, lado), Image.Resampling.LANCZOS, color=fundo)
            quadros.append(rgb)
            tempos.append(q.info.get("duration") or 100)

    if len(quadros) > P.TELA_MAX_QUADROS:
        passo = len(quadros) / P.TELA_MAX_QUADROS
        novos_q, novos_t = [], []
        for i in range(P.TELA_MAX_QUADROS):
            a, b = int(i * passo), int((i + 1) * passo)
            novos_q.append(quadros[a])
            novos_t.append(sum(tempos[a:b]))
        quadros, tempos = novos_q, novos_t

    return [para_rgb565(q) for q in quadros], tempos


def para_rgb565(img):
    px = img.convert("RGB").tobytes()
    dados = bytearray()
    for i in range(0, len(px), 3):
        dados += P.rgb565(px[i], px[i + 1], px[i + 2])
    return bytes(dados)
