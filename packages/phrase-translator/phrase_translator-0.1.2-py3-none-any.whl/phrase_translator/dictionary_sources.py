# pylint: disable=R0903

"""A default collection of DictionarySources."""
import json
from collections import defaultdict
from os import remove
from os.path import exists
from typing import Dict, List, Set

import wn  # type: ignore
from wn import Synset

from phrase_translator.phrase_translator import DictionarySource
from phrase_translator.types import Language, Translation


class FileDictionarySource(DictionarySource):
    """A simple dictionary source for reading from .dict files."""

    SEPARATOR: str = " -> "
    COMMENT: str = "#"
    LANGUAGE_INDICATOR = "lang: "

    def __init__(self, dictionary_files: List[str]) -> None:
        self.__dictionary_files: List[str] = dictionary_files
        self.__translations: Dict[str, Set[Translation]] = defaultdict(set)

        self.__load_files()

    def __raise_syntax_error(self, index: int, line: str):
        """Raises .dict Syntax Error."""
        raise SyntaxError(
            "Malformed Translation on line " + str(index + 1) + ": " + line
        )

    def __load_files(self) -> None:
        for dictionary_path in self.__dictionary_files:
            with open(dictionary_path, "r", encoding="utf-8") as dictionary_file:
                source_language = Language.UNKNOWN
                target_language = Language.UNKNOWN

                for index, line in enumerate(dictionary_file):
                    line = line.replace("\n", "")

                    if not line:
                        continue

                    if line.startswith(self.COMMENT):
                        continue

                    if line.startswith(self.LANGUAGE_INDICATOR):
                        lang_splits = line[len(self.LANGUAGE_INDICATOR) :].split(
                            self.SEPARATOR
                        )

                        if len(lang_splits) != 2:
                            self.__raise_syntax_error(index, line)

                        source_language = Language(lang_splits[0])
                        target_language = Language(lang_splits[1])

                    splits = line.split(self.SEPARATOR)

                    if len(splits) != 2:
                        self.__raise_syntax_error(index, line)

                    self.__translations[splits[0]].add(
                        Translation(
                            splits[0], splits[1], source_language, target_language
                        )
                    )

    def _provide_translations(self, phrase: str) -> Set[Translation]:
        return self.__translations[phrase]


class WikiExtractDictionarySource(DictionarySource):
    """A dictionary source based on dumps from
    https://github.com/tatuylonen/wiktextract"""

    DUMP_SUFFIX = ".json"
    CACHE_SUFFIX = "_cached.dict"

    def __init__(self, dump_paths: List[str], use_cached: bool = True) -> None:
        self.__dump_paths: List[str] = dump_paths
        self.__use_cached: bool = use_cached

        self.__load_files()

    def __load_files(self) -> None:
        self.__file_dictionary_sources: List[FileDictionarySource] = []

        for path_string in self.__dump_paths:
            cache_path = path_string.replace(self.DUMP_SUFFIX, self.CACHE_SUFFIX)
            if not exists(cache_path) or not self.__use_cached:
                self.__build_cache_dict(path_string, cache_path)

            self.__file_dictionary_sources.append(FileDictionarySource([cache_path]))

    def __build_cache_dict(self, dump_path: str, cache_path: str) -> None:
        if not self.__use_cached and exists(cache_path):
            remove(cache_path)

        with open(dump_path, "r", encoding="utf-8") as dump_file, open(
            cache_path, "w+", encoding="utf-8"
        ) as cache_file:
            for line in dump_file:
                data = json.loads(line)

                senses = data["senses"]

                for sense in senses:
                    if "translations" in sense:
                        for translation in sense["translations"]:
                            if "word" in translation:
                                cache_file.write(
                                    data["word"]
                                    + FileDictionarySource.SEPARATOR
                                    + translation["word"]
                                    + "\n"
                                )

    def _provide_translations(self, phrase: str) -> Set[Translation]:
        results = set()

        for fds in self.__file_dictionary_sources:
            for translation in fds.translate_phrase(phrase):
                results.add(translation)

        return results


class WordnetDictionarySource(DictionarySource):
    """A dictionary source based on multilingual wordnets"""

    def __init__(self, wordnets=None) -> None:

        if wordnets is None:
            wordnets = ["odenet:1.4", "oewn:2021", "omw:1.4", "cili:1.0"]

        self.__expand_string = " ".join(wordnets)

        self.__wordnet_ids = wordnets
        self.__wordnets = []

        invalid_ids = []
        for wordnet_id in self.__wordnet_ids:
            try:
                wn.download(wordnet_id)

                self.__wordnets.append(
                    wn.Wordnet(wordnet_id, expand=self.__expand_string)
                )
            except wn.Error:
                invalid_ids.append(wordnet_id)

        for id in invalid_ids:
            self.__wordnet_ids.remove(id)

    def _provide_translations(self, phrase: str) -> Set[Translation]:
        result: Set[Translation] = set()

        start_synsets: Set[Synset] = set()

        for wordnet in self.__wordnets:
            wn_synsets = wordnet.synsets(phrase)

            start_synsets = start_synsets.union(wn_synsets)

        for synset in start_synsets:
            source_language = Language(synset.lexicon().language)

            for wordnet_id in self.__wordnet_ids:
                for translated_synset in synset.translate(wordnet_id):
                    target_language = Language(translated_synset.lexicon().language)

                    for lemma in translated_synset.lemmas():
                        result.add(
                            Translation(phrase, lemma, source_language, target_language)
                        )

        return result
