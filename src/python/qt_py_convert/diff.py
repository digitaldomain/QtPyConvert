from qt_py_convert.color import ANSI, SUPPORTS_COLOR, color_text


class Chunk(object):
    """
    Chunk object maintains the split value and the key that was used to split
        it from the next Chunk object.
    """
    def __init__(self, value, sep_method):
        super(Chunk, self).__init__()
        self.value = value
        self.sep = sep_method

    def __repr__(self):
        return "<Chunk value:\"%s\" sep:\"%s\">" % (self.value, self.sep)

    def __eq__(self, other):
        if isinstance(other, Chunk):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.value)


def chunk_str(msg, sep=(" ", ".", ",", "(")):
    """
    chunk_str will take a string and a tuple of separators and recursively
        split the string into Chunk objects that record which separator was
        used to split it.
    :param msg: The string that we want to break apart.
    :type msg: str
    :param sep: Tuple of separators that you split on.
    :type sep: tuple[str...]
    :return: List of Chunk objects.
    :rtype: list[Chunk]
    """
    parts = [(part, sep[0]) for part in msg.split(sep[0])]
    out = []
    if len(sep) <= 1:
        return [Chunk(p[0], p[1]) for p in parts]
    for part, prev_split in parts:
        resulting_parts = chunk_str(part, sep=sep[1:])
        if len(resulting_parts) == 1:
            out.append(Chunk(part, prev_split))
        else:
            for resulting_chunk in resulting_parts[:-1]:
                out.append(resulting_chunk)
            out.append(
                Chunk(resulting_parts[-1].value, prev_split)
            )
            # out.append((resulting_parts, prev_split))
    out[-1].sep = ""
    return out


def _match(first_list, second_list):
    output = []
    for first_index, _chunk in enumerate(first_list):
        if _chunk in second_list:
            output.append([first_index, second_list.index(_chunk.value)])
    return output


def _equalize(first, second, sep=(" ", ".", ",", "(")):
    """
    equalize will take the two strings and attempt to build to lists of
        Chunks where the list are of equal lengths.

    :param first: First string that you want to compare.
    :type first: str
    :param second: Second string that you want to compare.
    :type second: str
    :param sep: Tuple of separators that you split on.
    :type sep: tuple[str...]
    :return: Tuple of two lists of Chunks
    :rtype: tuple[list[Chunk]]
    """
    first_chunk_list = chunk_str(first, sep=sep)
    second_chunk_list = chunk_str(second, sep=sep)
    matches = _match(first_chunk_list, second_chunk_list)
    if matches:
        if len(second_chunk_list) <= len(first_chunk_list):
            for first_loc, second_loc in matches:
                for _ in range(first_loc - second_loc):
                    second_chunk_list.insert(
                        second_loc - 1, Chunk("", "")
                    )
            while len(second_chunk_list) < len(first_chunk_list):
                second_chunk_list.append(Chunk("", ""))
        else:
            for first_loc, second_loc in matches:
                for _ in range(second_loc - first_loc):
                    first_chunk_list.insert(
                        first_loc - 1, Chunk("", "")
                    )
            while len(first_chunk_list) < len(second_chunk_list):
                first_chunk_list.append(Chunk("", ""))
    else:
        if not len(first_chunk_list) == len(second_chunk_list):
            if len(first_chunk_list) > len(second_chunk_list):
                larger = first_chunk_list
                smaller = second_chunk_list
            else:
                larger = second_chunk_list
                smaller = first_chunk_list

            for count in range(len(larger) - len(smaller)):
                smaller.append(Chunk("", ""))

    return first_chunk_list, second_chunk_list


def highlight_diffs(first, second, sep=(" ", ".", ",", "(")):
    if not SUPPORTS_COLOR:
        return first, second
    first_chunks, second_chunks = _equalize(first, second, sep=sep)
    first_out = ""
    second_out = ""
    for first_chunk, second_chunk in zip(first_chunks, second_chunks):
        if first_chunk != second_chunk:
            if first_chunk.value:
                first_out += color_text(
                    color=ANSI.colors.green,
                    text=first_chunk.value,
                    style=ANSI.styles.strong
                )
            if first_chunk.sep:
                first_out += color_text(
                    color=ANSI.colors.gray,
                    text=first_chunk.sep,
                )

            if second_chunk.value:
                second_out += color_text(
                    color=ANSI.colors.green,
                    text=second_chunk.value,
                    style=ANSI.styles.strong
                )
            if second_chunk.sep:
                second_out += color_text(
                    color=ANSI.colors.gray,
                    text=second_chunk.sep,
                )
        else:
            if first_chunk.value:
                first_out += color_text(
                    color=ANSI.colors.gray,
                    text=first_chunk.value,
                )
            if first_chunk.sep:
                first_out += color_text(
                    color=ANSI.colors.gray,
                    text=first_chunk.sep,
                )

            if second_chunk.value:
                second_out += color_text(
                    color=ANSI.colors.gray,
                    text=second_chunk.value,
                )
            if second_chunk.sep:
                second_out += color_text(
                    color=ANSI.colors.gray,
                    text=second_chunk.sep,
                )
    return first_out, second_out
