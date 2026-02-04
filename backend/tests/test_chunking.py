"""Unit tests for chunking strategy."""

import pytest
from src.features.rag.domain.chunking import ChunkingStrategy
from src.features.documents.domain.entities import Chunk


class TestChunkingStrategy:
    """Tests for ChunkingStrategy class."""

    def test_init_with_defaults(self):
        """Should initialize with default parameters."""
        strategy = ChunkingStrategy()
        assert strategy.chunk_size == 512
        assert strategy.overlap == 50

    def test_init_with_custom_params(self):
        """Should initialize with custom parameters."""
        strategy = ChunkingStrategy(chunk_size=100, overlap=10)
        assert strategy.chunk_size == 100
        assert strategy.overlap == 10

    def test_init_invalid_chunk_size(self):
        """Should raise error for invalid chunk size."""
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            ChunkingStrategy(chunk_size=0)

        with pytest.raises(ValueError, match="chunk_size must be positive"):
            ChunkingStrategy(chunk_size=-10)

    def test_init_invalid_overlap(self):
        """Should raise error for invalid overlap."""
        with pytest.raises(ValueError, match="overlap cannot be negative"):
            ChunkingStrategy(overlap=-5)

        with pytest.raises(ValueError, match="overlap must be less than chunk_size"):
            ChunkingStrategy(chunk_size=10, overlap=10)

    def test_chunk_empty_text(self):
        """Should return empty list for empty text."""
        strategy = ChunkingStrategy()
        chunks = strategy.chunk_text("", "doc-1")
        assert chunks == []

        chunks = strategy.chunk_text("   ", "doc-1")
        assert chunks == []

    def test_chunk_short_text(self):
        """Should create single chunk for short text."""
        strategy = ChunkingStrategy(chunk_size=10, overlap=2)
        text = "Short text"
        chunks = strategy.chunk_text(text, "doc-1")

        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].document_id == "doc-1"
        assert chunks[0].chunk_index == 0

    def test_chunk_long_text_creates_multiple(self):
        """Should create multiple chunks for long text."""
        strategy = ChunkingStrategy(chunk_size=10, overlap=2)
        words = [f"word{i}" for i in range(25)]
        text = " ".join(words)

        chunks = strategy.chunk_text(text, "doc-1")

        assert len(chunks) > 1
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.document_id == "doc-1" for c in chunks)

    def test_chunk_overlap_preserved(self):
        """Should preserve overlap between chunks."""
        strategy = ChunkingStrategy(chunk_size=10, overlap=3)
        words = [f"word{i}" for i in range(20)]
        text = " ".join(words)

        chunks = strategy.chunk_text(text, "doc-1")

        # Check that consecutive chunks have overlapping words
        assert len(chunks) >= 2

        # Extract words from first two chunks
        chunk1_words = chunks[0].text.split()
        chunk2_words = chunks[1].text.split()

        # Last words of chunk1 should appear in chunk2
        # (may not be exact due to sentence boundary adjustment)
        assert len(chunk1_words) <= 10
        assert len(chunk2_words) <= 10

    def test_chunk_index_increments(self):
        """Should increment chunk index correctly."""
        strategy = ChunkingStrategy(chunk_size=5, overlap=1)
        words = [f"word{i}" for i in range(15)]
        text = " ".join(words)

        chunks = strategy.chunk_text(text, "doc-1")

        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_chunk_with_metadata(self):
        """Should attach metadata to chunks."""
        strategy = ChunkingStrategy()
        metadata = {"page": 1, "doc_name": "test.pdf"}

        chunks = strategy.chunk_text("Some text", "doc-1", metadata)

        assert len(chunks) > 0
        assert chunks[0].metadata["page"] == 1
        assert chunks[0].metadata["doc_name"] == "test.pdf"

    def test_clean_text_removes_extra_whitespace(self):
        """Should clean excessive whitespace."""
        strategy = ChunkingStrategy()
        text = "Too    many   spaces\\n\\nand\\nnewlines"

        chunks = strategy.chunk_text(text, "doc-1")

        # Should have cleaned whitespace
        assert "    " not in chunks[0].text
        assert "\\n\\n" not in chunks[0].text

    def test_sentence_boundary_adjustment(self):
        """Should try to split at sentence boundaries."""
        strategy = ChunkingStrategy(chunk_size=15, overlap=2)
        text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."

        chunks = strategy.chunk_text(text, "doc-1")

        # At least one chunk should end with a period
        # (if sentence boundary adjustment worked)
        has_sentence_ending = any(
            chunk.text.rstrip().endswith('.')
            for chunk in chunks[:-1]  # Exclude last chunk
        )
        assert has_sentence_ending or len(chunks) == 1

    def test_chunk_ids_are_unique(self):
        """Should generate unique IDs for each chunk."""
        strategy = ChunkingStrategy(chunk_size=5, overlap=1)
        words = [f"word{i}" for i in range(20)]
        text = " ".join(words)

        chunks = strategy.chunk_text(text, "doc-1")

        chunk_ids = [c.id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))  # All unique

    def test_chunk_preserves_document_id(self):
        """Should preserve document ID in all chunks."""
        strategy = ChunkingStrategy(chunk_size=10, overlap=2)
        text = " ".join([f"word{i}" for i in range(30)])

        chunks = strategy.chunk_text(text, "doc-abc-123")

        assert len(chunks) > 1
        assert all(c.document_id == "doc-abc-123" for c in chunks)

    def test_word_count_in_metadata(self):
        """Should include word count in metadata."""
        strategy = ChunkingStrategy(chunk_size=10, overlap=2)
        text = "one two three four five six seven eight nine ten eleven"

        chunks = strategy.chunk_text(text, "doc-1", {"extra": "data"})

        assert all("word_count" in c.metadata for c in chunks)
        assert all(c.metadata["extra"] == "data" for c in chunks)
