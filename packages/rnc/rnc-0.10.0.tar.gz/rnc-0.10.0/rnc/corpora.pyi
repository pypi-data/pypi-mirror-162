import asyncio
import csv
import logging
import os
import random
import re
import string
import time
import urllib.parse
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Callable, Generator, Iterator, List, Any, Optional, Tuple, Pattern, Union, Literal, Type

import bs4
import ujson

import rnc.corpora_requests as creq
import rnc.examples as expl


SORT_KEYS = Literal[
    'i_grtagging', 'random', 'i_grauthor', 'i_grcreated_inv',
    'i_grcreated', 'i_grbirthday_inv', 'i_grbirthday',
]
SEARCH_FORMATS = Literal['lexform', 'lexgramm']
OUTPUT_FORMATS = Literal['normal', 'kwic']


class Corpus(ABC):
    """ Base class for Corpora """

    def __init__(self,
                 query: Optional[Union[dict, str]] = None,
                 p_count: Optional[int] = None,
                 file: Optional[Union[str, Path]] = None,
                 *,
                 dpp: Optional[int] = None,
                 spd: Optional[int] = None,
                 text: Optional[SEARCH_FORMATS] = None,
                 out: Optional[OUTPUT_FORMATS] = None,
                 sort: Optional[SORT_KEYS] = None,
                 accent: Optional[int] = None,
                 kwsz: Optional[int] = None,
                 mycorp: Optional[str] = None,
                 ex_type: Optional[Type[expl.Example]] = None,
                 marker: Optional[Callable] = None,
                 **kwargs) -> None:
        """
         If the file exists, working with a local database.

         :param query: dict of str, words to search;
         {word1: {properties}, word2: {properties}...}.
         If you chose 'lexform' as a 'text' param, you must give here a string.
         :param p_count: int, count of pages to request.
         :param file: str or Path, filename of a local database.
         Optional, random filename by default.
         :keyword dpp: str or int, documents per page.
         Optional, 5 by default.
         :keyword spd: str or int, sentences per document.
         Optional, 10 by default.
         :keyword text: str, search format: 'lexgramm' or 'lexform'.
         Optional, 'lexgramm' by default.
         :keyword out: str, output format: 'normal' or 'kwic'.
         Optional, 'normal' bu default.
         :keyword kwsz: str or int, count of words in context;
         Optional param if 'out' is 'kwic'.
         :keyword sort: str, sort show order. See docs how to set it.
         Optional.
         :keyword mycorp: This is way to specify the sample of docs
         where you want to find sth. See docs how to set it. Optional.
         :keyword expand: str, if 'full', all part of doc will be shown.
         Now it doesn't work.
         :keyword accent: str or int, with accents on words or not:
         1 – with, 0 – without. Optional, 0 by default.
         :keyword marker: function, with which found words will be marked.
         Optional.

         :exception FileExistsError: if csv file is given but json file
         with config doesn't exist.
         :exception ValueError: if the query is empty; page count is a negative
         number; text, out or sort key is wrong.
         :exception NotImplementedError: if the corpus type in file isn't equal
         to corpus class type.
         """
        pass

    def _from_corpus(self,
                     query: Union[Dict[str, Any], str],
                     p_count: int,
                     *,
                     dpp: Optional[int] = None,
                     spd: Optional[int] = None,
                     text: Optional[SEARCH_FORMATS] = None,
                     out: Optional[OUTPUT_FORMATS] = None,
                     sort: Optional[SORT_KEYS] = None,
                     accent: Optional[int] = None,
                     kwsz: Optional[int] = None,
                     mycorp: Optional[str] = None,
                     **kwargs) -> None:
        """ Set given values to the object. If the file does not exist.
        Params the same as in the init method.

        :exception ValueError: if the query is empty; pages count is a negative
         number; out, sort, text key is wrong.
        """
        pass

    def _from_file(self) -> None:
        """ Load data and params from the local databases.
        If the file exists.

        :exception FileExistsError: if csv file with data or
         json file with config do not exist.
        """
        pass

    def _load_data(self) -> List[expl.Example]:
        """ Load data from csv file. """
        pass

    def _load_params(self) -> Dict[str, Any]:
        """ Load request params from json file. """
        pass

    @classmethod
    def set_dpp(cls, value: int) -> None: ...

    @classmethod
    def set_spd(cls, value: int) -> None: ...

    @classmethod
    def set_text(cls, value: str) -> None: ...

    @classmethod
    def set_sort(cls, value: str) -> None: ...

    @classmethod
    def set_out(cls, value: str) -> None: ...

    @classmethod
    def set_min(cls, value: int) -> None: ...

    @classmethod
    def set_max(cls, value: int) -> None: ...

    @classmethod
    def set_restrict_show(cls, value: Union[int, bool]) -> None:
        """ Set amount of showing examples.
        Show all examples if `False` given.
        """
        pass

    @staticmethod
    def _get_ambiguation(tag: bs4.element.Tag) -> str:
        """ Get pretty ambiguation from example.

        :return: 'disambiguated' or 'not disambiguated' or 'Not found'.
        """
        pass

    @staticmethod
    def _get_text(tag: bs4.element.Tag) -> str:
        """ Get pretty text from example and remove
        from there duplicate spaces.

        Here it is assumed, that all examples have text.
        """
        pass

    @staticmethod
    def _get_doc_url(tag: bs4.element.Tag) -> str:
        """ Get pretty doc url from example.

        :return: doc url or 'Not found'.
        """
        pass

    @staticmethod
    def _get_source(tag: bs4.element.Tag) -> str:
        """ Get pretty source from example.

        :return: examples source or 'Not found'.
        """
        pass

    @staticmethod
    def _parse_lexgramm_params(params: Union[dict, str],
                               join_inside_symbol: str,
                               with_braces: bool = False) -> str:
        """ Convert lexgramm params to str for HTTP request.

        :param join_inside_symbol: symbol to join params.
        :param with_braces: whether the braces
         will be added around the param.
        :return: joined with ',' params.
        """
        pass

    @staticmethod
    def _find_searched_words(tag: bs4.element.Tag) -> List[str]:
        """ Get found words, they are marked with 'g-em'
        parameter in the class name. Strip them.
        """
        # searched words are marked by class parameter 'g-em'
        pass

    @property
    def data(self) -> List[expl.Example]:
        """ Get list of all examples """
        pass

    @property
    def query(self) -> Union[Dict[str, dict], str]:
        """ Get requested words items (dict of words
        with params or str with words)
        """
        pass

    @property
    def forms_in_query(self) -> List[str]:
        """ Requested wordforms """


    @property
    def p_count(self) -> int:
        """ Requested count of pages """
        pass

    @property
    def file(self) -> Path:
        """ Get path to local database file. """
        pass

    @property
    def marker(self) -> Callable:
        """ Get function to mark found wordforms. """
        pass

    @property
    def params(self) -> Dict[str, Any]:
        """ Get all HTTP params """
        pass

    @property
    def found_wordforms(self) -> Dict[str, int]:
        """ Get info about found wordforms, {form: frequency}. """
        pass

    @property
    def url(self) -> str:
        """ Get URL to first page of RNC results. """
        pass

    @property
    def ex_type(self) -> Any:
        """ get type of Example objects """
        pass

    @property
    def amount_of_docs(self) -> Optional[int]:
        """ Get amount of documents, where the query was found
        or None if there's no this info.
        """
        pass

    @property
    def amount_of_contexts(self) -> Optional[int]:
        """ Get amount of contexts, where the query was found
        or None if there's no this info.
        """
        pass

    @property
    def graphic_link(self) -> Optional[str]:
        """ Get the link to the graphic
        or None if there's no this info.
        """
        pass

    @staticmethod
    def _get_where_query_found(content: bs4.element.Tag) -> Dict[str, Any]:
        """ Get converted to int amount of found docs and contexts. """
        pass

    @staticmethod
    def _get_graphic_url(content: bs4.element.Tag) -> Optional[str]:
        """ Get URL to the graphic. """
        pass

    def _get_additional_info(self, first_page: Optional[str] = None) -> None:
        """ Get additional info (amount of found
        docs and contexts, link to the graphic).
        """
        pass

    async def _get_additional_info_async(self, first_page: Optional[str] = None) -> None:
        """ Get additional info (amount of found
        docs and contexts, link to the graphic).
        """
        pass

    def _page_parser_and_ex_type(self) -> None:
        """ Add 'parser' and 'ex_type' params.
        They are depended on 'out' tag.
        """
        pass

    def _query_to_http(self) -> None:
        """ Convert the query to HTTP tags, add them to params.

        :exception ValueError: if the query is not
        str however out is lexform;
        """
        pass

    def _add_wordforms(self, forms: List[str]) -> None:
        """ Add found wordforms to counter. """
        pass

    @abstractmethod
    def _parse_doc(self, doc: bs4.element.Tag) -> List[expl.Example]:
        """ Parse the doc to list of Examples.

        Parsing depends on the subcorpus,
         the method redefined at the descendants.
        """
        pass

    @abstractmethod
    def _parse_example(self, *args, **kwargs) -> expl.Example:
        """ Parse the example to Example object.

        Parsing depends on the subcorpus,
         the method redefined at the descendants.
        """
        pass

    def _parse_kwic_example(self,
                            left: bs4.element.Tag,
                            center: bs4.element.Tag,
                            right: bs4.element.Tag) -> expl.KwicExample:
        pass

    def _parse_page_kwic(self, page: str) -> List[expl.KwicExample]:
        """ Parse page if 'out' is 'kwic'.

        :exception ValueError: if the content not found.
        """
        pass

    def _parse_page_normal(self, page: str) -> List[expl.Example]:
        """ Parse page if 'out' is 'normal'. """
        pass

    def _parse_all_pages(self, pages: List[str]) -> List[expl.Example]:
        """ Parse all pages. """
        pass

    def _data_to_csv(self) -> None:
        """ Dump the data to csv file.
        Here it is assumed that the data exist.
        """
        pass

    def _params_to_json(self) -> None:
        """ Write the request params to json file.

        Here it is assumed that these params exist.
        """
        pass

    def dump(self) -> None:
        """ Write the data to csv file, request params to json file.

        :return: None.
        :exception RuntimeError: If there are no data, params or files exist.
        """
        pass

    def request_examples(self) -> None:
        """ Request examples, parse them and update the data.

        If there are no results found, last page does not exist,
        params or query is wrong then exception.

        :return: None.

        :exception RuntimeError: if the data still exist.
        """
        pass

    async def request_examples_async(self) -> None:
        """ Request examples, parse them and update the data.

        If there are no results found, last page does not exist,
        params or query is wrong then exception.

        :return: None.

        :exception RuntimeError: if the data still exist.
        """
        pass

    def copy(self) -> Corpus: ...

    def sort_data(self,
                  *,
                  key: Optional[Callable] = None,
                  reverse: bool = False,
                  **kwargs) -> None:
        """ Sort the data by using a key.

        :keyword key: func to sort, called to Example objects,
        by default – len.
        :keyword reverse: bool, whether the data will sort in reversed order,
         by default – False.

        :exception TypeError: if the key is uncallable.
        """
        pass

    def pop(self, index: int) -> expl.Example:
        """ Remove and return element from data at the index. """
        pass

    def shuffle(self) -> None:
        """ Shuffle list of examples. """
        pass

    def clear(self) -> None:
        """ Clear examples list. """
        pass

    def filter(self, key: Callable) -> None:
        """ Remove some items, that are not satisfied the key.

        :param key: callable, it will be used to Example
        objects inside the data list.
        :return: None.
        """
        pass

    def findall(self,
                pattern: Union[Pattern, str],
                *args) -> Generator[Tuple[expl.Example, List[str]], None, None]:
        """ Apply the pattern to the examples' text with re.findall.
        Yield all examples which are satisfy the pattern and match.
        """
        pass

    def finditer(self,
                 pattern: Union[Pattern, str],
                 *args) -> Generator[Tuple[expl.Example, Any], None, None]:
        """ Apply the pattern to the examples' text with re.finditer.
        Yield all examples which are satisfy the pattern and match.
        """
        pass

    def __repr__(self) -> str:
        """ Format:
                Classname
                Length
                Database filename
                Request params
                Pages count
                Request
        """
        pass

    def __str__(self) -> str:
        """
        :return: info about Corpus and enumerated examples.
        """
        pass

    def __len__(self) -> int: ...

    def __bool__(self) -> bool: ...

    def __call__(self) -> None:
        """ All the same to request_examples() """
        pass

    def __iter__(self) -> Iterator: ...

    def __contains__(self, item: expl.Example) -> bool:
        """ Whether the Corpus obj contains the Example obj.

        :param item: obj with the same ex_type.

        :exception TypeError: if wrong type (different Example) given.
        """
        pass

    def __getattr__(self, item: str) -> Optional[Union[str, int, List]]:
        """ Get request param.

        :return: param value or None if it does not exist.
        """
        pass

    def __getitem__(self, item: Union[int, slice]) -> Any:
        r""" Get example from data or create
         new obj with sliced data.

         Examples:
         =========
         .. code-block:: python
             >>> corp = MainCorpus(...)
             # get second example (1 is index, not number!)
             >>> corp[1]
             # create new copus with the first 50 example
             >>> new_corp = corp[:50]

        :return: one example or new obj with the same class and sliced data.
        :exception TypeError: if wrong type given.
        """
        pass

    def __setitem__(self, index: int, new_example: expl.Example) -> None:
        """ Change the example.

        Examples:
        >>> corp = MainCorpus(...)
        >>> corp[10] = MainExample(...)

        :exception TypeError: if wrong type given.
        """
        pass

    def __delitem__(self, key: Union[int, slice]) -> None:
        """ Delete example at the index or
         remove several ones using slice.

        Examples:
        >>> corp = MainCoprus(...)
        # delete forth example (3 is index, not number!)
        >>> del corp[3]
        # delete all examples after 10th
        >>> del corp[10:]
        # delete all exampes at even indexes from 0 to 10
        >>> del corp[0:10:2]

        :param key: int or slice, address of item(s) to delete.
        """
        pass


class MainCorpus(Corpus):
    def __init__(self,
                 query: Optional[Union[dict, str]] = None,
                 p_count: Optional[int] = None,
                 file: Optional[Union[str, Path]] = None,
                 *,
                 dpp: Optional[int] = None,
                 spd: Optional[int] = None,
                 text: Optional[SEARCH_FORMATS] = None,
                 out: Optional[OUTPUT_FORMATS] = None,
                 sort: Optional[SORT_KEYS] = None,
                 accent: Optional[int] = None,
                 kwsz: Optional[int] = None,
                 mycorp: Optional[str] = None,
                 marker: Optional[Callable] = None,
                 **kwargs) -> None:
        """
         If the file exists, working with a local database.

         :param query: dict of str, words to search;
         {word1: {properties}, word2: {properties}...}.
         If you chose 'lexform' as a 'text' param, you must give here a string.
         :param p_count: int, count of pages to request.
         :param file: str or Path, filename of a local database.
         Optional, random filename by default.
         :keyword dpp: str or int, documents per page.
         Optional, 5 by default.
         :keyword spd: str or int, sentences per document.
         Optional, 10 by default.
         :keyword text: str, search format: 'lexgramm' or 'lexform'.
         Optional, 'lexgramm' by default.
         :keyword out: str, output format: 'normal' or 'kwic'.
         Optional, 'normal' bu default.
         :keyword kwsz: str or int, count of words in context;
         Optional param if 'out' is 'kwic'.
         :keyword sort: str, sort show order. See docs how to set it.
         Optional.
         :keyword mycorp: This is way to specify the sample of docs
         where you want to find sth. See docs how to set it. Optional.
         :keyword expand: str, if 'full', all part of doc will be shown.
         Now it doesn't work.
         :keyword accent: str or int, with accents on words or not:
         1 – with, 0 – without. Optional, 0 by default.
         :keyword marker: function, with which found words will be marked.
         Optional.

         :exception FileExistsError: if csv file is given but json file
         with config doesn't exist.
         :exception ValueError: if the query is empty; page count is a negative
         number; text, out or sort key is wrong.
         :exception NotImplementedError: if the corpus type in file isn't equal
         to corpus class type.
         """
        pass

    def _parse_example(self, example: bs4.element.Tag) -> expl.MainExample: ... # type: ignore

    def _parse_doc(self, doc: bs4.element.Tag) -> List[expl.MainExample]: ... # type: ignore

    def _from_corpus(self,
                     query: Union[Dict[str, Any], str],
                     p_count: int,
                     *,
                     dpp: Optional[int] = None,
                     spd: Optional[int] = None,
                     text: Optional[SEARCH_FORMATS] = None,
                     out: Optional[OUTPUT_FORMATS] = None,
                     sort: Optional[SORT_KEYS] = None,
                     accent: Optional[int] = None,
                     kwsz: Optional[int] = None,
                     mycorp: Optional[str] = None,
                     **kwargs) -> None:
        """ Set given values to the object. If the file does not exist.
        Params the same as in the init method.

        :exception ValueError: if the query is empty; pages count is a negative
         number; out, sort, text key is wrong.
        """
        pass

    def _from_file(self) -> None:
        """ Load data and params from the local databases.
        If the file exists.

        :exception FileExistsError: if csv file with data or
         json file with config do not exist.
        """
        pass

    def _load_data(self) -> List[expl.MainExample]: # type: ignore
        """ Load data from csv file. """
        pass

    def _load_params(self) -> Dict[str, Any]:
        """ Load request params from json file. """
        pass

    @classmethod
    def set_dpp(cls, value: int) -> None:
        ...

    @classmethod
    def set_spd(cls, value: int) -> None:
        ...

    @classmethod
    def set_text(cls, value: str) -> None:
        ...

    @classmethod
    def set_sort(cls, value: str) -> None:
        ...

    @classmethod
    def set_out(cls, value: str) -> None:
        ...

    @classmethod
    def set_min(cls, value: int) -> None:
        ...

    @classmethod
    def set_max(cls, value: int) -> None:
        ...

    @classmethod
    def set_restrict_show(cls, value: Union[int, bool]) -> None:
        """ Set amount of showing examples.
        Show all examples if `False` given.
        """
        pass

    @staticmethod
    def _get_ambiguation(tag: bs4.element.Tag) -> str:
        """ Get pretty ambiguation from example.

        :return: 'disambiguated' or 'not disambiguated' or 'Not found'.
        """
        pass

    @staticmethod
    def _get_text(tag: bs4.element.Tag) -> str:
        """ Get pretty text from example and remove
        from there duplicate spaces.

        Here it is assumed, that all examples have text.
        """
        pass

    @staticmethod
    def _get_doc_url(tag: bs4.element.Tag) -> str:
        """ Get pretty doc url from example.

        :return: doc url or 'Not found'.
        """
        pass

    @staticmethod
    def _get_source(tag: bs4.element.Tag) -> str:
        """ Get pretty source from example.

        :return: examples source or 'Not found'.
        """
        pass

    @staticmethod
    def _parse_lexgramm_params(params: Union[dict, str],
                               join_inside_symbol: str,
                               with_braces: bool = False) -> str:
        """ Convert lexgramm params to str for HTTP request.

        :param join_inside_symbol: symbol to join params.
        :param with_braces: whether the braces
         will be added around the param.
        :return: joined with ',' params.
        """
        pass

    @staticmethod
    def _find_searched_words(tag: bs4.element.Tag) -> List[str]:
        """ Get found words, they are marked with 'g-em'
        parameter in the class name. Strip them.
        """
        # searched words are marked by class parameter 'g-em'
        pass

    @property
    def data(self) -> List[expl.MainExample]:
        """ Get list of all examples """
        pass

    @property
    def query(self) -> Union[Dict[str, dict], str]:
        """ Get requested words items (dict of words
        with params or str with words)
        """
        pass

    @property
    def forms_in_query(self) -> List[str]:
        """ Requested wordforms """

    @property
    def p_count(self) -> int:
        """ Requested count of pages """
        pass

    @property
    def file(self) -> Path:
        """ Get path to local database file. """
        pass

    @property
    def marker(self) -> Callable:
        """ Get function to mark found wordforms. """
        pass

    @property
    def params(self) -> Dict[str, Any]:
        """ Get all HTTP params """
        pass

    @property
    def found_wordforms(self) -> Dict[str, int]:
        """ Get info about found wordforms, {form: frequency}. """
        pass

    @property
    def url(self) -> str:
        """ Get URL to first page of RNC results. """
        pass

    @property
    def ex_type(self) -> Any:
        """ get type of Example objects """
        pass

    @property
    def amount_of_docs(self) -> Optional[int]:
        """ Get amount of documents, where the query was found
        or None if there's no this info.
        """
        pass

    @property
    def amount_of_contexts(self) -> Optional[int]:
        """ Get amount of contexts, where the query was found
        or None if there's no this info.
        """
        pass

    @property
    def graphic_link(self) -> Optional[str]:
        """ Get the link to the graphic
        or None if there's no this info.
        """
        pass

    @staticmethod
    def _get_where_query_found(content: bs4.element.Tag) -> Dict[str, Any]:
        """ Get converted to int amount of found docs and contexts. """
        pass

    @staticmethod
    def _get_graphic_url(content: bs4.element.Tag) -> Optional[str]:
        """ Get URL to the graphic. """
        pass

    def _get_additional_info(self, first_page: Optional[str] = None) -> None:
        """ Get additional info (amount of found
        docs and contexts, link to the graphic).
        """
        pass

    async def _get_additional_info_async(self, first_page: Optional[str] = None) -> None:
        """ Get additional info (amount of found
        docs and contexts, link to the graphic).
        """
        pass

    def _page_parser_and_ex_type(self) -> None:
        """ Add 'parser' and 'ex_type' params.
        They are depended on 'out' tag.
        """
        pass

    def _query_to_http(self) -> None:
        """ Convert the query to HTTP tags, add them to params.

        :exception ValueError: if the query is not
        str however out is lexform;
        """
        pass

    def _add_wordforms(self, forms: List[str]) -> None:
        """ Add found wordforms to counter. """
        pass

    def _parse_kwic_example(self,
                            left: bs4.element.Tag,
                            center: bs4.element.Tag,
                            right: bs4.element.Tag) -> expl.KwicExample:
        pass

    def _parse_page_kwic(self, page: str) -> List[expl.KwicExample]:
        """ Parse page if 'out' is 'kwic'.

        :exception ValueError: if the content not found.
        """
        pass

    def _parse_page_normal(self, page: str) -> List[expl.Example]:
        """ Parse page if 'out' is 'normal'. """
        pass

    def _parse_all_pages(self, pages: List[str]) -> List[expl.Example]:
        """ Parse all pages. """
        pass

    def _data_to_csv(self) -> None:
        """ Dump the data to csv file.
        Here it is assumed that the data exist.
        """
        pass

    def _params_to_json(self) -> None:
        """ Write the request params to json file.

        Here it is assumed that these params exist.
        """
        pass

    def dump(self) -> None:
        """ Write the data to csv file, request params to json file.

        :return: None.
        :exception RuntimeError: If there are no data, params or files exist.
        """
        pass

    def request_examples(self) -> None:
        """ Request examples, parse them and update the data.

        If there are no results found, last page does not exist,
        params or query is wrong then exception.

        :return: None.

        :exception RuntimeError: if the data still exist.
        """
        pass

    async def request_examples_async(self) -> None:
        """ Request examples, parse them and update the data.

        If there are no results found, last page does not exist,
        params or query is wrong then exception.

        :return: None.

        :exception RuntimeError: if the data still exist.
        """
        pass

    def copy(self) -> Corpus:
        ...

    def sort_data(self,
                  *,
                  key: Optional[Callable] = None,
                  reverse: bool = False,
                  **kwargs) -> None:
        """ Sort the data by using a key.

        :keyword key: func to sort, called to Example objects,
        by default – len.
        :keyword reverse: bool, whether the data will sort in reversed order,
         by default – False.

        :exception TypeError: if the key is uncallable.
        """
        pass

    def pop(self, index: int) -> expl.MainExample:
        """ Remove and return element from data at the index. """
        pass

    def shuffle(self) -> None:
        """ Shuffle list of examples. """
        pass

    def clear(self) -> None:
        """ Clear examples list. """
        pass

    def filter(self, key: Callable) -> None:
        """ Remove some items, that are not satisfied the key.

        :param key: callable, it will be used to Example
        objects inside the data list.
        :return: None.
        """
        pass

    def findall(self,
                pattern: Union[Pattern, str],
                *args) -> Generator[Tuple[expl.MainExample, List[str]], None, None]:
        """ Apply the pattern to the examples' text with re.findall.
        Yield all examples which are satisfy the pattern and match.
        """
        pass

    def finditer(self,
                 pattern: Union[Pattern, str],
                 *args) -> Generator[Tuple[expl.MainExample, Any], None, None]:
        """ Apply the pattern to the examples' text with re.finditer.
        Yield all examples which are satisfy the pattern and match.
        """
        pass

    def __repr__(self) -> str:
        """ Format:
                Classname
                Length
                Database filename
                Request params
                Pages count
                Request
        """
        pass

    def __str__(self) -> str:
        """
        :return: info about Corpus and enumerated examples.
        """
        pass

    def __len__(self) -> int:
        ...

    def __bool__(self) -> bool:
        ...

    def __call__(self) -> None:
        """ All the same to request_examples() """
        pass

    def __iter__(self) -> Iterator[expl.MainExample]:
        ...

    def __contains__(self, item: expl.MainExample) -> bool: # type: ignore
        """ Whether the Corpus obj contains the Example obj.

        :param item: obj with the same ex_type.

        :exception TypeError: if wrong type (different Example) given.
        """
        pass

    def __getattr__(self, item: str) -> Optional[Union[str, int, List]]:
        """ Get request param.

        :return: param value or None if it does not exist.
        """
        pass

    def __getitem__(self, item: Union[int, slice]) -> Any:
        r""" Get example from data or create
         new obj with sliced data.

         Examples:
         =========
         .. code-block:: python
             >>> corp = MainCorpus(...)
             # get second example (1 is index, not number!)
             >>> corp[1]
             # create new copus with the first 50 example
             >>> new_corp = corp[:50]

        :return: one example or new obj with the same class and sliced data.
        :exception TypeError: if wrong type given.
        """
        pass

    def __setitem__(self, index: int, new_example: expl.MainExample) -> None:
        """ Change the example.

        Examples:
        >>> corp = MainCorpus(...)
        >>> corp[10] = MainExample(...)

        :exception TypeError: if wrong type given.
        """
        pass

    def __delitem__(self, key: Union[int, slice]) -> None:
        """ Delete example at the index or
         remove several ones using slice.

        Examples:
        >>> corp = MainCoprus(...)
        # delete forth example (3 is index, not number!)
        >>> del corp[3]
        # delete all examples after 10th
        >>> del corp[10:]
        # delete all exampes at even indexes from 0 to 10
        >>> del corp[0:10:2]

        :param key: int or slice, address of item(s) to delete.
        """
        pass


class NGrams(Corpus):
    # env = sas1_2
    pass


class BiGrams(NGrams):
    pass


class ThreeGrams(NGrams):
    pass


class FourGrams(NGrams):
    pass


class FiveGrams(NGrams):
    pass


class SyntaxCorpus(Corpus):
    pass


class Paper2000Corpus(MainCorpus):
    _MODE = 'paper'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, ex_type=expl.Paper2000Example)
        self._params['mode'] = self._MODE


class PaperRegionalCorpus(MainCorpus):
    _MODE = 'regional'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, ex_type=expl.PaperRegionalExample)
        self._params['mode'] = self._MODE


class ParallelCorpus(Corpus):
    _MODE = 'para'

    def __init__(self, *args, **kwargs) -> None:
        # for descendants
        ex_type = kwargs.pop('ex_type', expl.ParallelExample)
        super().__init__(*args, **kwargs, ex_type=ex_type)
        self._params['mode'] = self._MODE

    def _parse_text(self,
                    lang: str,
                    text: bs4.element.Tag) -> Any:
        """ Parse one element of the pair: original – translation.
        Means parse original or translation.
        """
        src = Corpus._get_source(text)
        txt = Corpus._get_text(text)
        # remove source from text
        txt = txt[:txt.index(src)]
        txt = txt[:txt.rindex('[')].strip()

        found_words = Corpus._find_searched_words(text)

        new_txt = self.ex_type(
            txt={lang: txt},
            src=src,
            ambiguation=Corpus._get_ambiguation(text),
            found_wordforms=found_words,
            doc_url=Corpus._get_doc_url(text)
        )
        new_txt.mark_found_words(self.marker)
        return new_txt

    def _parse_example(self, # type: ignore
                       tag: bs4.element.Tag) -> expl.Example:
        """ Parse a pair: original – translation to Example. """
        # this example is expected to have default args
        result_example = self.ex_type()

        langs = tag.find_all('td', {'class': "para-lang"})
        texts = tag.find_all('li')
        for lang, text in zip(langs, texts):
            lang = lang.text.strip()
            new_txt = self._parse_text(lang, text)
            result_example += new_txt
        return result_example

    def _parse_doc(self,
                   doc: bs4.element.Tag) -> List:
        """ Parse one document. """
        res = []
        for example in doc.find_all('table', {'class': 'para'}):
            new_ex = self._parse_example(example)
            res += [new_ex]
            self._add_wordforms(new_ex.found_wordforms)
        return res

    def _load_data(self) -> List:
        """ Load data from csv file. """
        if self.out == 'kwic':
            return super()._load_data()

        with self.file.open('r', encoding='utf-8') as f:
            dm = self._DATA_W_DELIMITER
            qch = self._DATA_W_QUOTCHAR
            reader = csv.reader(f, delimiter=dm, quotechar=qch)

            columns = next(reader)
            end_lang_tags = columns.index('source')
            lang_tags = columns[:end_lang_tags]
            data = []

            for row in reader:
                # to create dict {lang: text in the lang}
                langs = {}
                for num, lang in enumerate(lang_tags):
                    langs[lang] = row[num]

                new_ex = self.ex_type(langs, *row[end_lang_tags:])
                data += [new_ex]

                self._add_wordforms(new_ex.found_wordforms)

        return data


class MultilingualParaCorpus(ParallelCorpus):
    _MODE = 'multi'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs,
                         ex_type=expl.MultilingualParaExample)
        self._params['mode'] = self._MODE

    def _from_file(self) -> None:
        msg = f"Working with files not supported" \
              f" in {self.__class__.__name__}"
        logger.error(msg)
        raise NotImplementedError(msg)

    def dump(self) -> None:
        msg = f"Working with files not supported" \
              f" in {self.__class__.__name__}"
        logger.error(msg)
        raise NotImplementedError(msg)


class TutoringCorpus(MainCorpus):
    _MODE = 'school'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs,
                         ex_type=expl.TutoringExample)
        self._params['mode'] = self._MODE


class DialectalCorpus(MainCorpus):
    _MODE = 'dialect'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         ex_type=expl.DialectalExample)
        self._params['mode'] = self._MODE


# save lines
class PoeticCorpus(Corpus):
    pass


class SpokenCorpus(MainCorpus):
    _MODE = 'spoken'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         ex_type=expl.SpokenExample)
        self._params['mode'] = self._MODE


class AccentologicalCorpus(MainCorpus):
    _MODE = 'accent'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         ex_type=expl.AccentologicalExample)
        self._params['mode'] = self._MODE


class MultimodalCorpus(Corpus):
    MEDIA_FOLDER = Corpus.DATA_FOLDER / 'media'
    _MODE = 'murco'

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, ex_type=expl.MultimodalExample)
        self._params['mode'] = self._MODE

    def _parse_example(self, # type: ignore
                       example: bs4.element.Tag
                       ) -> Tuple[str, str, str, list, str]:
        """ Parse example get text, source etc. """
        src = Corpus._get_source(example)
        txt = Corpus._get_text(example)
        txt = txt[:txt.index(src)]
        txt = txt[:txt.rindex('[')].strip()

        doc_url = Corpus._get_doc_url(example)
        ambiguation = Corpus._get_ambiguation(example)
        found_words = Corpus._find_searched_words(example)

        return txt, src, ambiguation, found_words, doc_url

    def _parse_media(self,
                     media: bs4.element.Tag) -> Tuple[str, str]:
        """ Get link to the media file and filepath. """
        try:
            media_link = media.find('a')['href']
        except Exception:
            raise

        media_link, filename = media_link.split('?name=')
        return media_link, self.MEDIA_FOLDER / filename

    def _parse_doc(self,
                   doc: bs4.element.Tag) -> List[Any]:
        """ Parse the documents to examples. """
        try:
            media = doc.find('td', {'valign': 'top'})
            example = doc.find('td', {'class': 'murco-snippet'})
        except ValueError:
            return []
        examples = []

        media_url, filename = self._parse_media(media)
        # for example in example:
        data_from_example = self._parse_example(example)

        new_ex = self.ex_type(*data_from_example, media_url, filename)
        new_ex.mark_found_words(self.marker)
        self._add_wordforms(new_ex.found_wordforms)
        examples += [new_ex]

        return examples

    def download_all(self) -> None:
        """ Download all files. """
        os.makedirs(self.MEDIA_FOLDER, exist_ok=True)

        urls_to_names = [
            (example._media_url, example.filepath)
            for example in self
        ]
        creq.download_docs(urls_to_names)

    async def download_all_async(self) -> None:
        """ Download all files. """
        os.makedirs(self.MEDIA_FOLDER, exist_ok=True)

        urls_to_names = [
            (example._media_url, example.filepath)
            for example in self
        ]
        await creq.download_docs_async(urls_to_names)


class MultiPARCCorpus(Corpus):
    pass


class HistoricalCorpus(Corpus):
    pass
