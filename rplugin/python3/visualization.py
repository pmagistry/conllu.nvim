# -*- coding:utf-8 -*-
# originaly Modified for hanlp from https://github.com/tylerneylon/explacy
from collections import defaultdict
from pprint import pprint


def make_table(rows, insert_header=False):
    col_widths = [max(len(s) for s in col) for col in zip(*rows[1:])]
    rows[0] = [x[:l] for x, l in zip(rows[0], col_widths)]
    fmt = '\t'.join('%%-%ds' % width for width in col_widths)
    if insert_header:
        rows.insert(1, ['─' * width for width in col_widths])
    return '\n'.join(fmt % tuple(row) for row in rows)


def _start_end(arrow):
    start, end = arrow['from'], arrow['to']
    mn = min(start, end)
    mx = max(start, end)
    return start, end, mn, mx


def pretty_tree_horizontal(arrows, _do_print_debug_info=False):
    """Print the dependency tree horizontally

    Args:
      arrows: 
      _do_print_debug_info:  (Default value = False)

    Returns:

    """
    # Set the base height; these may increase to allow room for arrowheads after this.
    arrows_with_deps = defaultdict(set)
    for i, arrow in enumerate(arrows):
        arrow['underset'] = set()
        if _do_print_debug_info:
            print('Arrow %d: "%s" -> "%s"' % (i, arrow['from'], arrow['to']))
        num_deps = 0
        start, end, mn, mx = _start_end(arrow)
        for j, other in enumerate(arrows):
            if arrow is other:
                continue
            o_start, o_end, o_mn, o_mx = _start_end(other)
            if ((start == o_start and mn <= o_end <= mx) or
                    (start != o_start and mn <= o_start <= mx)):
                num_deps += 1
                if _do_print_debug_info:
                    print('%d is over %d' % (i, j))
                arrow['underset'].add(j)
        arrow['num_deps_left'] = arrow['num_deps'] = num_deps
        arrows_with_deps[num_deps].add(i)

    if _do_print_debug_info:
        print('')
        print('arrows:')
        pprint(arrows)

        print('')
        print('arrows_with_deps:')
        pprint(arrows_with_deps)

    # Render the arrows in characters. Some heights will be raised to make room for arrowheads.
    sent_len = (max([max(arrow['from'], arrow['to']) for arrow in arrows]) if arrows else 0) + 1
    lines = [[] for i in range(sent_len)]
    num_arrows_left = len(arrows)
    while num_arrows_left > 0:

        assert len(arrows_with_deps[0])

        arrow_index = arrows_with_deps[0].pop()
        arrow = arrows[arrow_index]
        src, dst, mn, mx = _start_end(arrow)

        # Check the height needed.
        height = 3
        if arrow['underset']:
            height = max(arrows[i]['height'] for i in arrow['underset']) + 1
        height = max(height, 3, len(lines[dst]) + 3)
        arrow['height'] = height

        if _do_print_debug_info:
            print('')
            print('Rendering arrow %d: "%s" -> "%s"' % (arrow_index,
                                                        arrow['from'],
                                                        arrow['to']))
            print('  height = %d' % height)

        goes_up = src > dst

        # Draw the outgoing src line.
        if lines[src] and len(lines[src]) < height:
            lines[src][-1].add('w')
        while len(lines[src]) < height - 1:
            lines[src].append(set(['e', 'w']))
        if len(lines[src]) < height:
            lines[src].append({'e'})
        lines[src][height - 1].add('n' if goes_up else 's')

        # Draw the incoming dst line.
        lines[dst].append(u'►')
        while len(lines[dst]) < height:
            lines[dst].append(set(['e', 'w']))
        lines[dst][-1] = set(['e', 's']) if goes_up else set(['e', 'n'])

        # Draw the adjoining vertical line.
        for i in range(mn + 1, mx):
            while len(lines[i]) < height - 1:
                lines[i].append(' ')
            lines[i].append(set(['n', 's']))

        # Update arrows_with_deps.
        for arr_i, arr in enumerate(arrows):
            if arrow_index in arr['underset']:
                arrows_with_deps[arr['num_deps_left']].remove(arr_i)
                arr['num_deps_left'] -= 1
                arrows_with_deps[arr['num_deps_left']].add(arr_i)

        num_arrows_left -= 1

    return render_arrows(lines)


def render_arrows(lines):
    arr_chars = {'ew': u'─',
                 'ns': u'│',
                 'en': u'└',
                 'es': u'┌',
                 'enw': u'┴',
                 'ensw': u'┼',
                 'ens': u'├',
                 'esw': u'┬'}
    # Convert the character lists into strings.
    max_len = max(len(line) for line in lines)
    for i in range(len(lines)):
        lines[i] = [arr_chars[''.join(sorted(ch))] if type(ch) is set else ch for ch in lines[i]]
        lines[i] = ''.join(reversed(lines[i]))
        lines[i] = ' ' * (max_len - len(lines[i])) + lines[i]
    return lines


def render_span(begin, end, unidirectional=False):
    if end - begin == 1:
        return ['───►']
    elif end - begin == 2:
        return [
            '──┐',
            '──┴►',
        ] if unidirectional else [
            '◄─┐',
            '◄─┴►',
        ]

    rows = []
    for i in range(begin, end):
        if i == (end - begin) // 2 + begin:
            rows.append('  ├►')
        elif i == begin:
            rows.append('──┐' if unidirectional else '◄─┐')
        elif i == end - 1:
            rows.append('──┘' if unidirectional else '◄─┘')
        else:
            rows.append('  │')
    return rows
