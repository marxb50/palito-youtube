"""Regressões de portabilidade, contato de elenco e duração da mixagem."""
from array import array
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave


SKILL = Path(__file__).resolve().parents[1] / 'palito-youtube'
FABRICA = SKILL / 'fabrica-palito'


class TesteFabrica(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raiz = Path(tmp.name)

    def executar(self, *args):
        subprocess.run(
            [sys.executable, '-B', str(FABRICA / 'fabrica.py'), *map(str, args)],
            cwd=self.raiz, check=True, capture_output=True, text=True,
        )

    def metadados(self, mp4):
        return json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries',
            'stream=codec_type,nb_frames,avg_frame_rate:format=duration', '-of', 'json', str(mp4),
        ]))

    def test_renderiza_exemplo_mudo_em_outra_pasta(self):
        episodio = self.raiz / 'entrega'
        shutil.copytree(FABRICA / 'exemplos' / 'entrega', episodio, ignore=shutil.ignore_patterns('producao', '*.mp4'))
        self.executar('produzir', episodio, '--mudo', '--tamanho', '320x180')
        self.executar('revisar', episodio, '--mudo')

        mp4 = episodio / 'entrega-animatic.mp4'
        info = self.metadados(mp4)
        self.assertEqual(float(info['format']['duration']), 6)
        self.assertEqual(len(info['streams']), 1)
        self.assertEqual(info['streams'][0]['nb_frames'], '360')
        qa = next((episodio / 'producao').glob('revisao-*/qa.json'))
        self.assertIsNone(json.loads(qa.read_text(encoding='utf-8'))['ebur128_summary'])
        self.assertTrue(qa.with_name('planos-01.jpg').is_file())

    def test_efeitos_e_loudness_preservam_audio_no_final(self):
        episodio = self.raiz / 'frases'
        episodio.mkdir()
        taxa = 24000
        pcm = array('h', (
            round(4200 * math.sin(2 * math.pi * 810 * i / taxa))
            if taxa // 5 < i < taxa or 3 * taxa < i < 4 * taxa else 0
            for i in range(4 * taxa)
        ))
        with wave.open(str(episodio / 'voz.wav'), 'wb') as arquivo:
            arquivo.setparams((1, 2, taxa, len(pcm), 'NONE', 'not compressed'))
            arquivo.writeframes(pcm.tobytes())

        planos = [
            {'id': 'inicio', 'fala': 'Primeira frase.', 'mundo': 'creme',
             'elementos': [{'id': 'livro', 'tipo': 'livro', 'pos': [265, 333, 2]}]},
            {'id': 'fim', 'fala': 'Última frase.', 'mundo': 'kraft', 'entrada': 'folha', 'inicio_s': 2,
             'elementos': [{'id': 'livro', 'tipo': 'livro', 'pos': [563, 337, 2]}]},
        ]
        (episodio / 'episodio.json').write_text(
            json.dumps({'versao': 1, 'audio': 'voz.wav', 'planos': planos}, ensure_ascii=False),
            encoding='utf-8',
        )
        for opcoes in [('--sfx',), ('--lufs', '-16'), ('--sfx', '--lufs', '-16')]:
            with self.subTest(opcoes=opcoes):
                self.executar('produzir', episodio, '--tamanho', '320x180', *opcoes)
                mp4 = episodio / 'frases.mp4'
                self.assertEqual(float(self.metadados(mp4)['format']['duration']), 4)
                cauda = subprocess.check_output([
                    'ffmpeg', '-v', 'error', '-ss', '3.4', '-i', str(mp4), '-t', '0.3',
                    '-map', '0:a:0', '-ac', '1', '-f', 's16le', 'pipe:1',
                ])
                amostras = array('h', cauda)
                rms = math.sqrt(sum(v*v for v in amostras) / len(amostras))
                self.assertGreater(rms, 800)


if __name__ == '__main__':
    unittest.main()
