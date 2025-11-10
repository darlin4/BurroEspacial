"""Sound helper que intenta reproducir audio de forma segura.

Intenta reproducir con `playsound` en un hilo separado (como hace la
pantalla de portada). Si `playsound` no está disponible en el entorno,
intenta la alternativa nativa de Windows (`winsound`). Si ninguna está
disponible, la función no fallará — devolverá False.
"""

from typing import Optional
import threading
import os


class SoundHelper:
    @staticmethod
    def play_sound(path: str) -> bool:
        """Reproduce el archivo de sonido en background.

        Devuelve True si se lanzó la reproducción (o si el fichero existe
        y se programó la reproducción). No lanza excepciones al llamar.
        """
        try:
            if not os.path.exists(path):
                return False

            # Preferir playsound si está instalado (coherente con portada.py)
            try:
                from playsound import playsound

                def _play():
                    try:
                        playsound(path)
                    except Exception:
                        # no raise; playback can fail on headless envs
                        pass

                threading.Thread(target=_play, daemon=True).start()
                return True
            except Exception:
                pass

            # Fallback Windows
            try:
                import winsound

                def _play_win():
                    try:
                        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    except Exception:
                        pass

                threading.Thread(target=_play_win, daemon=True).start()
                return True
            except Exception:
                pass

            return False
        except Exception:
            return False


__all__ = ["SoundHelper"]
