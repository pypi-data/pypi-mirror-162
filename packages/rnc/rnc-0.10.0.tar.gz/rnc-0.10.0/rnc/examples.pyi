from pathlib import Path
from typing import Any, List, Union, Dict, Callable, Optional


class Example:
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> Any: ...

    @property
    def src(self) -> Any: ...

    @property
    def ambiguation(self) -> Any: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: Any) -> None: ...

    @src.setter # type: ignore
    def src(self, other: Any) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: Any) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> Any: ...

    def __eq__(self, other: object) -> bool: ... # type: ignore

    def __contains__(self, item: Any) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class KwicExample(Example):
    def __init__(self, left: str, center: str, right: str, src: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def left(self) -> str: ...

    @property
    def center(self) -> str: ...

    @property
    def right(self) -> str: ...

    @property
    def txt(self) -> str: ...

    @property
    def ambiguation(self) -> None:
        raise NotImplementedError()

    @property
    def data(self) -> Dict[str, Any]: ...

    @left.setter # type: ignore
    def left(self, other: Any) -> None: ...

    @center.setter # type: ignore
    def center(self, other: Any) -> None: ...

    @right.setter # type: ignore
    def right(self, other: Any) -> None: ...

    @txt.setter # type: ignore
    def txt(self, other: Any) -> None:
        raise NotImplementedError()

    def mark_found_words(self, marker: Callable) -> None: ...

    @property
    def src(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @src.setter # type: ignore
    def src(self, other: Any) -> None: ...

    def open_doc(self) -> None: ...

    def copy(self) -> KwicExample: ...

    def __eq__(self, other: KwicExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class MainExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> MainExample: ...

    def __eq__(self, other: MainExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class SyntaxExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> SyntaxExample: ...

    def __eq__(self, other: SyntaxExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class Paper2000Example(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> Paper2000Example: ...

    def __eq__(self, other: Paper2000Example) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class PaperRegionalExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> PaperRegionalExample: ...

    def __eq__(self, other: PaperRegionalExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class ParallelExample(Example):
    def __init__(self, txt: Dict[str, str] = None, src: str = '', ambiguation: str = '',
                 found_wordforms: Union[List[str], str] = None, doc_url: str = '') -> None:
        """
        :param txt: dict of str, {language tag: text}
        :param src: str, examples source.
        :param ambiguation: str, examples ambiguation.
        :param found_wordforms: list of str, examples found wordforms.
        :param doc_url: str, examples URL.
        """
        pass

    @property
    def txt(self) -> Dict[str, Any]:
        """ Get dict with texts.

        :return: dict of any types.
        """
        pass

    @txt.setter
    def txt(self, other: Any) -> None:
        """ Text setter not implemented to the ParallelExample """
        raise NotImplementedError()

    @property
    def data(self) -> Dict[str, Any]:
        """ There are all fields except for doc_url.
        Found wordforms joined with ', '.

        :return: dict with fields' names and their values.
        """
        pass

    def mark_found_words(self, marker: Callable) -> None:
        """ Mark found wordforms in the text with marker.

        :param marker: function to mark.
        :return: None.
        """
        pass

    @staticmethod
    def _best_src(f_src: str, s_src: str) -> str:
        """ Choose the best source, means
        there are two translations in it.

        :param f_src: str, first source.
        :param s_src: str, second source.
        :return: str, best of them.
        """
        pass

    def sort(self, key: Optional[Callable] = None, reverse: bool = False) -> None:
        """ Sort txt dict, allowing the key to
        items() from there.

        :param key: callable, key to sort. Sort by language tag by default.
        :param reverse: bool, whether sorting will be in reversed order.
        :return: None.
        """
        pass

    def copy(self) -> ParallelExample:
        """
        :return: copied obj.
        """
        pass

    def __contains__(self, item: str) -> bool:
        """ Whether the item is in the text.
        Registers equaled (if it is available).

        :param item: any type, item to check.
        :return: whether item is in text.
        """
        pass

    def __iadd__(self, other: ParallelExample) -> ParallelExample:
        """ Concatenate two examples:
            – join the texts

            – choose the best source, there are
            two translations there

            – choose where the text is disambiguated.

            – join found wordforms.

        :param other: instance of the same class.
        :return: self.
        :exception TypeError: if wrong type given.
        """
        pass

    def __getattr__(self, item: str) -> str:
        """ Get the text in language.

        :param item: str, language tag.
        :return: str or None, text in the language if exists.
        """
        pass

    def __getitem__(self, lang: str) -> str:
        """ Get text in the language.

        :param lang: str, language tag.
        :return: str or None, text in the language if exists.
        """
        pass

    def __setitem__(self, lang: str, txt: str) -> None:
        """ Change text in the language.

        :param lang: str, language tag.
        :param txt: any type, new text.
        :return: None.
        :exception ValueError: if the text in the language does not exist.
        """
        pass

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def __eq__(self, other: ParallelExample) -> bool: ... # type: ignore

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class MultilingualParaExample(ParallelExample):
    def __init__(self, txt: Dict[str, str] = None, src: str = '', ambiguation: str = '',
                 found_wordforms: Union[List[str], str] = None, doc_url: str = '') -> None:
        """
        :param txt: dict of str, {language tag: text}
        :param src: str, examples source.
        :param ambiguation: str, examples ambiguation.
        :param found_wordforms: list of str, examples found wordforms.
        :param doc_url: str, examples URL.
        """
        pass

    @property
    def txt(self) -> Dict[str, Any]:
        """ Get dict with texts.

        :return: dict of any types.
        """
        pass

    @txt.setter
    def txt(self, other: Any) -> None:
        """ Text setter not implemented to the ParallelExample """
        raise NotImplementedError()

    @property
    def data(self) -> Dict[str, Any]:
        """ There are all fields except for doc_url.
        Found wordforms joined with ', '.

        :return: dict with fields' names and their values.
        """
        pass

    def mark_found_words(self, marker: Callable) -> None:
        """ Mark found wordforms in the text with marker.

        :param marker: function to mark.
        :return: None.
        """
        pass

    @staticmethod
    def _best_src(f_src: str, s_src: str) -> str:
        """ Choose the best source, means
        there are two translations in it.

        :param f_src: str, first source.
        :param s_src: str, second source.
        :return: str, best of them.
        """
        pass

    def sort(self, key: Optional[Callable] = None, reverse: bool = False) -> None:
        """ Sort txt dict, allowing the key to
        items() from there.

        :param key: callable, key to sort. Sort by language tag by default.
        :param reverse: bool, whether sorting will be in reversed order.
        :return: None.
        """
        pass

    def copy(self) -> MultilingualParaExample:
        """
        :return: copied obj.
        """
        pass

    def __contains__(self, item: str) -> bool:
        """ Whether the item is in the text.
        Registers equaled (if it is available).

        :param item: any type, item to check.
        :return: whether item is in text.
        """
        pass

    def __iadd__(self, other: MultilingualParaExample) -> MultilingualParaExample: # type: ignore
        """ Concatenate two examples:
            – join the texts

            – choose the best source, there are
            two translations there

            – choose where the text is disambiguated.

            – join found wordforms.

        :param other: instance of the same class.
        :return: self.
        :exception TypeError: if wrong type given.
        """
        pass

    def __getattr__(self, item: str) -> str:
        """ Get the text in language.

        :param item: str, language tag.
        :return: str or None, text in the language if exists.
        """
        pass

    def __getitem__(self, lang: str) -> str:
        """ Get text in the language.

        :param lang: str, language tag.
        :return: str or None, text in the language if exists.
        """
        pass

    def __setitem__(self, lang: str, txt: str) -> None:
        """ Change text in the language.

        :param lang: str, language tag.
        :param txt: any type, new text.
        :return: None.
        :exception ValueError: if the text in the language does not exist.
        """
        pass

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @txt.setter  # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter  # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter  # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def __eq__(self, other: MultilingualParaExample) -> bool: ... # type: ignore

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class TutoringExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> TutoringExample: ...

    def __eq__(self, other: TutoringExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class DialectalExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> DialectalExample: ...

    def __eq__(self, other: DialectalExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class PoeticExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> PoeticExample: ...

    def __eq__(self, other: PoeticExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class SpokenExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> SpokenExample: ...

    def __eq__(self, other: SpokenExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class AccentologicalExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> AccentologicalExample: ...

    def __eq__(self, other: AccentologicalExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class MultimodalExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str],
                 doc_url: str, media_url: str, filename: str) -> None:
        """
        :param txt: str, example's text.
        :param src: str, example's source.
        :param ambiguation: str, example's ambiguation.
        :param found_wordforms: list of str, None or str joined with ', ',
        example's found wordforms.
        :param doc_url: str, example's url.
        :param media_url: str, URL to example's media file.
        :param filename: str or Path, default name of the file (from RNC).
        :return: None.
        """
        pass

    @property
    def filepath(self) -> Path:
        """ Get the path to the local file.

        :return: Path to the file.
        """
        pass

    @filepath.setter
    def filepath(self, other: Union[str, Path]) -> None:
        """ Set new path to the local file.

        ATTENTION: if the file exists it will not be moved to
        the new path. You should call 'download_file()' again.

        :param other: str or Path, new path to the local file.
        :return: None.
        """
        pass

    @property
    def columns(self) -> List[str]:
        """ For csv writing.

        :return: list of str, names of columns.
        """
        pass

    @property
    def items(self) -> List[Any]:
        """ For csv writing.

        :return: list of any types, values of columns.
        """
        pass

    def download_file(self) -> None:
        """ Download the media file.

        :return: None.
        """
        pass

    async def download_file_async(self) -> None: ...

    def copy(self) -> MultimodalExample: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def __eq__(self, other: MultimodalExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class MultiPARCExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> MultiPARCExample: ...

    def __eq__(self, other: MultiPARCExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...


class HistoricalExample(Example):
    def __init__(self, txt: str, src: str, ambiguation: str, found_wordforms: Union[List[str], str], doc_url: str) -> None: ...

    @property
    def txt(self) -> str: ...

    @property
    def src(self) -> str: ...

    @property
    def ambiguation(self) -> str: ...

    @property
    def doc_url(self) -> str: ...

    @property
    def found_wordforms(self) -> List[str]: ...

    @property
    def columns(self) -> List[str]: ...

    @property
    def items(self) -> List[Any]: ...

    @property
    def data(self) -> Dict[str, Any]: ...

    @txt.setter # type: ignore
    def txt(self, other: str) -> None: ...

    @src.setter # type: ignore
    def src(self, other: str) -> None: ...

    @ambiguation.setter # type: ignore
    def ambiguation(self, other: str) -> None: ...

    def open_doc(self) -> None: ...

    def mark_found_words(self, marker: Callable) -> None: ...

    def copy(self) -> HistoricalExample: ...

    def __eq__(self, other: HistoricalExample) -> bool: ... # type: ignore

    def __contains__(self, item: str) -> bool: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __bool__(self) -> bool: ...
