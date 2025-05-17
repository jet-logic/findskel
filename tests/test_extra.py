#!/bin/env python3
import unittest


def reverse_iterative(head: tuple[str, object] | None) -> tuple[str, object] | None:
    prev = None
    current = head

    while current is not None:
        data, next_node = current
        # Update the current node to point to `prev` (reversing the link)
        new_current = (data, prev)
        # Move `prev` and `current` forward
        prev = new_current
        current = next_node

    return prev  # `prev` is the new head


def traverse_iterative(head):
    current = head
    while current is not None:
        data, next_node = current
        yield data
        current = next_node  # Move to next node


def prepend(head: tuple[str, object] | None, new_data: str) -> tuple[str, object]:
    """Adds a new node at the beginning of the linked list."""
    return (new_data, head)


class TestExtra(unittest.TestCase):
    def test_linked_list_iter(self):
        linked_list = ("A", ("B", ("C", None)))
        s = "-".join(traverse_iterative(linked_list))
        self.assertEqual(s, "A-B-C")

    def test_linked_list_prepend(self):
        # Example:
        linked_list = ("B", ("C", None))
        new_list = prepend(linked_list, "A")  # Adds "A" at the front
        s = "-".join(traverse_iterative(new_list))
        self.assertEqual(s, "A-B-C")

    def test_linked_list_reverse_iterative(self):
        # Example:
        linked_list = ("A", ("B", ("C", None)))
        s = "-".join(traverse_iterative(reverse_iterative(linked_list)))
        self.assertEqual(s, "C-B-A")


if __name__ == "__main__":
    unittest.main()
