from pathlib import Path
import music21 as m21
from music21.stream.base import Score, Part, Stream
from music21.note import NotRest
from tqdm import tqdm
# import converter21

# converter21.register()

type Melody = list[NotRest]


def parse_palestrina_krn(palestrina_krn_score_path: Path) -> Score:
    """
    Parse a Palestrina score from music21's humdrum kern file.
    The kern files were encoded using ISO-8859-1 (latin1)
    and its 0xe9 byte causes nuisance.
    """
    encoding = "ISO-8859-1"  # aka 'latin1'
    text: str = palestrina_krn_score_path.read_text(encoding)
    score: Score = m21.converter.parse(text)
    score.metadata.filePath = palestrina_krn_score_path
    return score


def extractMelodiesFromPart(part: Part) -> list[Melody]:
    notRests: list[NotRest | None] = (
        part.flatten().stripTies().findConsecutiveNotes(skipUnisons=True)
    )
    melodies: list[list[NotRest]] = []
    if notRests[0] is not None:
        melodies.append([])
    for notRest in notRests:
        if notRest:
            melodies[-1].append(notRest)
        else:
            melodies.append([])

    return melodies


def extractMelodiesfromScore(score: Score) -> list[Melody]:
    return [melody for part in score.parts for melody in extractMelodiesFromPart(part)]


if __name__ == "__main__":
    PATH = Path("public/scores/palestrina-melodies")
    FORMAT = "musicxml"  # "mei"

    """
    Check if path is there. If not, create.
    """
    (PATH / FORMAT).mkdir(parents=True, exist_ok=True)

    """
    Run loop through all the files.
    """
    scores: enumerate[Path] = enumerate(m21.corpus.getComposer("palestrina"))
    for i, path in tqdm(scores, desc="Parsing Palestrina Music21 scores:"):
        score = parse_palestrina_krn(path)
        melodies = extractMelodiesfromScore(score)
        for j, melody in enumerate(melodies):
            n = j + i * j
            stream: Stream[NotRest] = Stream()
            stream.timeSignature = None
            melody_offset = melody[0].offset
            stream.append(melody)
            stream.shiftElements(0)
            stream.show("text")
            stream.write(
                fmt=FORMAT,
                fp=PATH / FORMAT / f"melody_{n}.{FORMAT}",
            )
