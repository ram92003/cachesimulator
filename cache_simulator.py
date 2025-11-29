#!/usr/bin/env python3
"""
Cache Memory Simulation Program
================================
This program simulates both Direct-Mapped Cache and Fully Associative Cache
with detailed educational output suitable for Computer Organization and Architecture (COA) demonstrations.

Features:
- Direct-Mapped and Fully Associative cache modes
- Automatic calculation of tag, index, and offset bits
- Read/Write operations with hit/miss handling
- Write-through and Write-back strategies
- LRU (Least Recently Used) replacement policy for associative mode
- Detailed trace output for each memory access
- Comprehensive statistics tracking

Author: Cache Simulator for COA Viva
"""

import math
from collections import OrderedDict


class CacheBlock:
    """
    Represents a single cache block/line with all necessary metadata.
    
    Fields:
    - valid: Valid bit (1 if block contains valid data, 0 otherwise)
    - tag: Tag bits from the memory address
    - data: The actual data stored (simplified as memory address for this simulation)
    - dirty: Dirty bit (1 if block has been modified, 0 otherwise) - used in write-back policy
    """
    
    def __init__(self):
        self.valid = 0
        self.tag = None
        self.data = None
        self.dirty = 0
    
    def __repr__(self):
        return f"[V:{self.valid} T:{self.tag if self.tag is not None else '-'} D:{self.dirty} Data:{self.data if self.data is not None else '-'}]"


class CacheSimulator:
    """Base class for cache simulation with common functionality."""
    
    def __init__(self, cache_size, block_size, write_policy='write-through'):
        """
        Initialize cache parameters.
        
        Args:
            cache_size: Total size of cache in bytes
            block_size: Size of each cache block in bytes
            write_policy: 'write-through' or 'write-back'
        """
        self.cache_size = cache_size
        self.block_size = block_size
        self.num_blocks = cache_size // block_size
        self.write_policy = write_policy
        
        # Calculate address bit fields
        self.offset_bits = int(math.log2(block_size))
        
        # Statistics
        self.total_accesses = 0
        self.hits = 0
        self.misses = 0
        self.memory_reads = 0
        self.memory_writes = 0
        
    def decompose_address(self, address):
        """
        Extract offset bits from address (common to all cache types).
        
        Args:
            address: Memory address (integer)
            
        Returns:
            offset: Offset bits
        """
        offset_mask = (1 << self.offset_bits) - 1
        offset = address & offset_mask
        return offset
    
    def get_statistics(self):
        """Return comprehensive statistics."""
        hit_ratio = (self.hits / self.total_accesses * 100) if self.total_accesses > 0 else 0
        miss_ratio = (self.misses / self.total_accesses * 100) if self.total_accesses > 0 else 0
        
        return {
            'total_accesses': self.total_accesses,
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio,
            'miss_ratio': miss_ratio,
            'memory_reads': self.memory_reads,
            'memory_writes': self.memory_writes
        }
    
    def print_statistics(self):
        """Print formatted statistics."""
        stats = self.get_statistics()
        print("\n" + "="*70)
        print(" CACHE SIMULATION STATISTICS ".center(70, "="))
        print("="*70)
        print(f"Total Cache Accesses     : {stats['total_accesses']}")
        print(f"Cache Hits               : {stats['hits']}")
        print(f"Cache Misses             : {stats['misses']}")
        print(f"Hit Ratio                : {stats['hit_ratio']:.2f}%")
        print(f"Miss Ratio               : {stats['miss_ratio']:.2f}%")
        print(f"\nMemory Traffic:")
        print(f"  Memory Reads           : {stats['memory_reads']} (block fetches on miss)")
        print(f"  Memory Writes          : {stats['memory_writes']} (write-through + dirty evictions)")
        print(f"  Total Memory Accesses  : {stats['memory_reads'] + stats['memory_writes']}")
        print(f"\nWrite Policy             : {self.write_policy.upper()}")
        print("="*70 + "\n")


class DirectMappedCache(CacheSimulator):
    """
    Direct-Mapped Cache Implementation
    
    In Direct-Mapped Cache:
    - Each memory block maps to exactly ONE cache line
    - Mapping determined by: cache_line = (block_address) % (number_of_cache_lines)
    - Fast and simple, but can have conflicts when multiple addresses map to same line
    - Address decomposition: | Tag | Index | Offset |
      * Index bits: Used to select the cache line
      * Tag bits: Stored in cache line to identify which block is currently stored
      * Offset bits: Used to select byte within the block
    """
    
    def __init__(self, cache_size, block_size, write_policy='write-through'):
        super().__init__(cache_size, block_size, write_policy)
        
        # Calculate index bits for direct-mapped cache
        self.index_bits = int(math.log2(self.num_blocks))
        self.tag_bits = 32 - self.index_bits - self.offset_bits  # Assuming 32-bit addresses
        
        # Initialize cache lines
        self.cache = [CacheBlock() for _ in range(self.num_blocks)]
        
        print(f"\n{'='*70}")
        print(" DIRECT-MAPPED CACHE CONFIGURATION ".center(70, "="))
        print(f"{'='*70}")
        print(f"Cache Size               : {cache_size} bytes")
        print(f"Block Size               : {block_size} bytes")
        print(f"Number of Cache Lines    : {self.num_blocks}")
        print(f"Write Policy             : {write_policy.upper()}")
        print(f"\nAddress Bit Breakdown (32-bit address):")
        print(f"  Tag bits               : {self.tag_bits} bits")
        print(f"  Index bits             : {self.index_bits} bits")
        print(f"  Offset bits            : {self.offset_bits} bits")
        print(f"{'='*70}\n")
    
    def decompose_address(self, address):
        """
        Decompose address into tag, index, and offset for direct-mapped cache.
        
        Args:
            address: Memory address (integer)
            
        Returns:
            tuple: (tag, index, offset)
        """
        offset_mask = (1 << self.offset_bits) - 1
        offset = address & offset_mask
        
        index_mask = (1 << self.index_bits) - 1
        index = (address >> self.offset_bits) & index_mask
        
        tag = address >> (self.offset_bits + self.index_bits)
        
        return tag, index, offset
    
    def access(self, address, operation='read', data=None):
        """
        Simulate a cache access (read or write).
        
        Args:
            address: Memory address to access
            operation: 'read' or 'write'
            data: Data to write (if operation is 'write')
        """
        self.total_accesses += 1
        tag, index, offset = self.decompose_address(address)
        
        print(f"\n{'─'*70}")
        print(f"Access #{self.total_accesses}: {operation.upper()} Address 0x{address:08X} (Decimal: {address})")
        print(f"{'─'*70}")
        print(f"Address Decomposition:")
        print(f"  Tag    = {tag:>10} (0x{tag:X})")
        print(f"  Index  = {index:>10} (Cache Line #{index})")
        print(f"  Offset = {offset:>10} (Byte offset in block)")
        
        cache_line = self.cache[index]
        
        # Check for cache hit or miss
        if cache_line.valid == 1 and cache_line.tag == tag:
            # CACHE HIT
            self.hits += 1
            print(f"\n✓ CACHE HIT!")
            print(f"  Found valid block with matching tag in Line {index}")
            
            if operation == 'write':
                self._handle_write_hit(index, address, data)
            else:
                print(f"  Data retrieved from cache: {cache_line.data}")
        else:
            # CACHE MISS
            self.misses += 1
            print(f"\n✗ CACHE MISS!")
            
            if cache_line.valid == 1:
                print(f"  Line {index} occupied by different block (Tag: {cache_line.tag})")
                print(f"  EVICTION: Replacing old block")
                
                # If write-back policy and dirty bit is set, write back to memory
                if self.write_policy == 'write-back' and cache_line.dirty == 1:
                    self.memory_writes += 1
                    print(f"  ⚠ Dirty block detected! Writing back to memory")
                    print(f"    Memory writes count: {self.memory_writes}")
            else:
                print(f"  Line {index} is empty (invalid)")
            
            # Fetch block from memory and place in cache
            self._fetch_from_memory(index, tag, address, operation, data)
    
    def _handle_write_hit(self, index, address, data):
        """Handle write operation on cache hit."""
        cache_line = self.cache[index]
        
        if self.write_policy == 'write-through':
            # Write-Through: Update cache AND memory immediately
            cache_line.data = address if data is None else data
            self.memory_writes += 1
            print(f"  WRITE-THROUGH: Data written to cache AND memory")
            print(f"    Memory writes count: {self.memory_writes}")
            cache_line.dirty = 0  # No need for dirty bit in write-through
        else:
            # Write-Back: Update cache only, mark as dirty
            cache_line.data = address if data is None else data
            cache_line.dirty = 1
            print(f"  WRITE-BACK: Data written to cache only")
            print(f"    Dirty bit set to 1 (will write to memory on eviction)")
    
    def _fetch_from_memory(self, index, tag, address, operation, data):
        """Fetch block from memory and update cache."""
        cache_line = self.cache[index]
        
        print(f"  Fetching block from memory...")
        self.memory_reads += 1  # Read from memory
        print(f"    Memory reads: {self.memory_reads}")
        
        # Update cache line
        cache_line.valid = 1
        cache_line.tag = tag
        cache_line.data = address if data is None else data
        
        if operation == 'write':
            if self.write_policy == 'write-through':
                cache_line.dirty = 0
                self.memory_writes += 1  # Additional write to memory
                print(f"  Block loaded and WRITE-THROUGH executed")
                print(f"    Memory writes: {self.memory_writes}")
            else:
                cache_line.dirty = 1
                print(f"  Block loaded with dirty bit = 1 (write-back pending)")
        else:
            cache_line.dirty = 0
            print(f"  Block loaded into cache line {index}")
        
        print(f"  Cache Line {index} updated: {cache_line}")
    
    def display_cache(self):
        """Display current state of all cache lines."""
        print(f"\n{'='*70}")
        print(" CACHE STATE ".center(70, "="))
        print(f"{'='*70}")
        print(f"{'Line':<6} {'Valid':<7} {'Tag':<12} {'Dirty':<7} {'Data':<20}")
        print(f"{'─'*70}")
        for i, block in enumerate(self.cache):
            tag_str = f"0x{block.tag:X}" if block.tag is not None else "-"
            data_str = f"0x{block.data:X}" if block.data is not None else "-"
            print(f"{i:<6} {block.valid:<7} {tag_str:<12} {block.dirty:<7} {data_str:<20}")
        print(f"{'='*70}\n")


class FullyAssociativeCache(CacheSimulator):
    """
    Fully Associative Cache Implementation
    
    In Fully Associative Cache:
    - A memory block can be placed in ANY cache line
    - No index bits needed - entire address (except offset) is the tag
    - Requires searching ALL cache lines for a match
    - More flexible than direct-mapped, reduces conflict misses
    - Uses replacement policy (LRU) when cache is full
    - Address decomposition: | Tag | Offset |
      * Tag bits: Identify which block is stored (no index needed!)
      * Offset bits: Select byte within the block
    
    Replacement Policy - LRU (Least Recently Used):
    - Tracks the order of cache line usage
    - When cache is full, evicts the least recently used line
    - Implemented using OrderedDict to maintain access order
    """
    
    def __init__(self, cache_size, block_size, write_policy='write-through'):
        super().__init__(cache_size, block_size, write_policy)
        
        # In fully associative, no index bits - only tag and offset
        self.tag_bits = 32 - self.offset_bits  # Assuming 32-bit addresses
        
        # Initialize cache with OrderedDict for LRU tracking
        # Key: line number, Value: CacheBlock
        self.cache = OrderedDict()
        for i in range(self.num_blocks):
            self.cache[i] = CacheBlock()
        
        # Track access order for LRU
        self.lru_counter = 0
        
        print(f"\n{'='*70}")
        print(" FULLY ASSOCIATIVE CACHE CONFIGURATION ".center(70, "="))
        print(f"{'='*70}")
        print(f"Cache Size               : {cache_size} bytes")
        print(f"Block Size               : {block_size} bytes")
        print(f"Number of Cache Lines    : {self.num_blocks} (any block can go anywhere!)")
        print(f"Replacement Policy       : LRU (Least Recently Used)")
        print(f"Write Policy             : {write_policy.upper()}")
        print(f"\nAddress Bit Breakdown (32-bit address):")
        print(f"  Tag bits               : {self.tag_bits} bits")
        print(f"  Index bits             : 0 bits (no index in fully associative!)")
        print(f"  Offset bits            : {self.offset_bits} bits")
        print(f"{'='*70}\n")
    
    def decompose_address(self, address):
        """
        Decompose address into tag and offset for fully associative cache.
        
        Args:
            address: Memory address (integer)
            
        Returns:
            tuple: (tag, offset)
        """
        offset_mask = (1 << self.offset_bits) - 1
        offset = address & offset_mask
        
        tag = address >> self.offset_bits
        
        return tag, offset
    
    def _find_block(self, tag):
        """
        Search all cache lines for a matching tag.
        
        Returns:
            line_number if found, None otherwise
        """
        for line_num, block in self.cache.items():
            if block.valid == 1 and block.tag == tag:
                return line_num
        return None
    
    def _find_empty_line(self):
        """Find first empty (invalid) cache line."""
        for line_num, block in self.cache.items():
            if block.valid == 0:
                return line_num
        return None
    
    def _evict_lru(self):
        """
        Evict the least recently used cache line.
        Returns the line number of the evicted line.
        """
        # In OrderedDict, first item is the least recently used
        lru_line = next(iter(self.cache))
        return lru_line
    
    def _update_lru(self, line_num):
        """Move accessed line to end (most recently used)."""
        self.cache.move_to_end(line_num)
    
    def access(self, address, operation='read', data=None):
        """
        Simulate a cache access (read or write) with LRU replacement.
        
        Args:
            address: Memory address to access
            operation: 'read' or 'write'
            data: Data to write (if operation is 'write')
        """
        self.total_accesses += 1
        tag, offset = self.decompose_address(address)
        
        print(f"\n{'─'*70}")
        print(f"Access #{self.total_accesses}: {operation.upper()} Address 0x{address:08X} (Decimal: {address})")
        print(f"{'─'*70}")
        print(f"Address Decomposition:")
        print(f"  Tag    = {tag:>10} (0x{tag:X})")
        print(f"  Offset = {offset:>10} (Byte offset in block)")
        print(f"\nSearching all {self.num_blocks} cache lines for matching tag...")
        
        # Search for tag in all cache lines
        hit_line = self._find_block(tag)
        
        if hit_line is not None:
            # CACHE HIT
            self.hits += 1
            print(f"\n✓ CACHE HIT!")
            print(f"  Found valid block with matching tag in Line {hit_line}")
            
            # Update LRU order
            self._update_lru(hit_line)
            print(f"  LRU Update: Line {hit_line} moved to most recently used")
            
            cache_line = self.cache[hit_line]
            
            if operation == 'write':
                self._handle_write_hit(hit_line, address, data)
            else:
                print(f"  Data retrieved from cache: {cache_line.data}")
        else:
            # CACHE MISS
            self.misses += 1
            print(f"\n✗ CACHE MISS!")
            print(f"  Tag {tag} not found in any cache line")
            
            # Try to find empty line first
            empty_line = self._find_empty_line()
            
            if empty_line is not None:
                # Use empty line
                print(f"  Empty line found: Line {empty_line}")
                target_line = empty_line
            else:
                # Cache full - evict LRU line
                target_line = self._evict_lru()
                evicted_block = self.cache[target_line]
                print(f"  Cache FULL! Applying LRU replacement policy")
                print(f"  EVICTION: Line {target_line} (LRU line) will be replaced")
                print(f"    Evicted block: Tag={evicted_block.tag}, Dirty={evicted_block.dirty}")
                
                # If write-back policy and dirty bit is set, write back to memory
                if self.write_policy == 'write-back' and evicted_block.dirty == 1:
                    self.memory_writes += 1
                    print(f"    ⚠ Dirty block detected! Writing back to memory")
                    print(f"    Memory writes count: {self.memory_writes}")
            
            # Fetch block from memory and place in target line
            self._fetch_from_memory(target_line, tag, address, operation, data)
            
            # Update LRU order
            self._update_lru(target_line)
    
    def _handle_write_hit(self, line_num, address, data):
        """Handle write operation on cache hit."""
        cache_line = self.cache[line_num]
        
        if self.write_policy == 'write-through':
            # Write-Through: Update cache AND memory immediately
            cache_line.data = address if data is None else data
            self.memory_writes += 1
            print(f"  WRITE-THROUGH: Data written to cache AND memory")
            print(f"    Memory writes count: {self.memory_writes}")
            cache_line.dirty = 0
        else:
            # Write-Back: Update cache only, mark as dirty
            cache_line.data = address if data is None else data
            cache_line.dirty = 1
            print(f"  WRITE-BACK: Data written to cache only")
            print(f"    Dirty bit set to 1 (will write to memory on eviction)")
    
    def _fetch_from_memory(self, line_num, tag, address, operation, data):
        """Fetch block from memory and update cache."""
        cache_line = self.cache[line_num]
        
        print(f"  Fetching block from memory...")
        self.memory_reads += 1  # Read from memory
        print(f"    Memory reads: {self.memory_reads}")
        
        # Update cache line
        cache_line.valid = 1
        cache_line.tag = tag
        cache_line.data = address if data is None else data
        
        if operation == 'write':
            if self.write_policy == 'write-through':
                cache_line.dirty = 0
                self.memory_writes += 1
                print(f"  Block loaded and WRITE-THROUGH executed")
                print(f"    Memory writes: {self.memory_writes}")
            else:
                cache_line.dirty = 1
                print(f"  Block loaded with dirty bit = 1 (write-back pending)")
        else:
            cache_line.dirty = 0
            print(f"  Block loaded into cache line {line_num}")
        
        print(f"  Cache Line {line_num} updated: {cache_line}")
    
    def display_cache(self):
        """Display current state of all cache lines with LRU order."""
        print(f"\n{'='*70}")
        print(" CACHE STATE (LRU order: top=LRU, bottom=MRU) ".center(70, "="))
        print(f"{'='*70}")
        print(f"{'Line':<6} {'Valid':<7} {'Tag':<15} {'Dirty':<7} {'Data':<20}")
        print(f"{'─'*70}")
        for line_num, block in self.cache.items():
            tag_str = f"0x{block.tag:X}" if block.tag is not None else "-"
            data_str = f"0x{block.data:X}" if block.data is not None else "-"
            print(f"{line_num:<6} {block.valid:<7} {tag_str:<15} {block.dirty:<7} {data_str:<20}")
        print(f"{'='*70}\n")


def print_header():
    """Print program header."""
    print("\n" + "="*70)
    print(" CACHE MEMORY SIMULATION PROGRAM ".center(70, "="))
    print("="*70)
    print(" For Computer Organization and Architecture (COA) Demonstration ".center(70))
    print("="*70)
    print("\nThis program simulates cache memory operations including:")
    print("  • Direct-Mapped Cache and Fully Associative Cache")
    print("  • Read/Write operations with Hit/Miss detection")
    print("  • Write-Through and Write-Back policies")
    print("  • LRU (Least Recently Used) replacement for Associative Cache")
    print("  • Detailed trace of each memory access")
    print("  • Comprehensive statistics tracking")
    print("="*70 + "\n")


def run_sample_demo():
    """Run a comprehensive sample demonstration."""
    print("\n" + "="*70)
    print(" SAMPLE DEMONSTRATION ".center(70, "="))
    print("="*70)
    
    # Demonstration 1: Direct-Mapped vs Fully Associative with conflict misses
    print("\n" + "="*70)
    print(" Demo 1: Direct-Mapped vs Fully Associative (Conflict Misses) ".center(70))
    print("="*70)
    print("\nCache Parameters: 16 bytes total, 4 bytes per block (4 cache lines)")
    print("Write Policy: Write-Back")
    print("Address Sequence: [0, 16, 32, 0, 16, 32, 0, 16]")
    print("\nNote: Addresses 0, 16, 32 all map to the SAME cache line in Direct-Mapped!")
    print("      But Fully Associative can place them in different lines.\n")
    
    addresses1 = [0, 16, 32, 0, 16, 32, 0, 16]
    
    # Direct-Mapped Demo
    print("\n" + "#"*70)
    print(" PART 1: DIRECT-MAPPED CACHE ".center(70, "#"))
    print("#"*70)
    
    dm_cache = DirectMappedCache(cache_size=16, block_size=4, write_policy='write-back')
    
    for i, addr in enumerate(addresses1):
        operation = 'write' if i % 4 == 0 else 'read'
        dm_cache.access(addr, operation=operation)
    
    dm_cache.display_cache()
    dm_cache.print_statistics()
    
    # Fully Associative Demo
    print("\n" + "#"*70)
    print(" PART 2: FULLY ASSOCIATIVE CACHE WITH LRU ".center(70, "#"))
    print("#"*70)
    
    fa_cache = FullyAssociativeCache(cache_size=16, block_size=4, write_policy='write-back')
    
    for i, addr in enumerate(addresses1):
        operation = 'write' if i % 4 == 0 else 'read'
        fa_cache.access(addr, operation=operation)
    
    fa_cache.display_cache()
    fa_cache.print_statistics()
    
    # Comparison
    print("\n" + "="*70)
    print(" COMPARISON SUMMARY (Demo 1) ".center(70, "="))
    print("="*70)
    dm_stats = dm_cache.get_statistics()
    fa_stats = fa_cache.get_statistics()
    
    print(f"{'Metric':<30} {'Direct-Mapped':<20} {'Fully Associative':<20}")
    print("─"*70)
    print(f"{'Cache Hits':<30} {dm_stats['hits']:<20} {fa_stats['hits']:<20}")
    print(f"{'Cache Misses':<30} {dm_stats['misses']:<20} {fa_stats['misses']:<20}")
    print(f"{'Hit Ratio':<30} {dm_stats['hit_ratio']:.2f}%{'':<15} {fa_stats['hit_ratio']:.2f}%")
    print(f"{'Memory Reads':<30} {dm_stats['memory_reads']:<20} {fa_stats['memory_reads']:<20}")
    print(f"{'Memory Writes':<30} {dm_stats['memory_writes']:<20} {fa_stats['memory_writes']:<20}")
    dm_total = dm_stats['memory_reads'] + dm_stats['memory_writes']
    fa_total = fa_stats['memory_reads'] + fa_stats['memory_writes']
    print(f"{'Total Memory Traffic':<30} {dm_total:<20} {fa_total:<20}")
    print("="*70)
    
    print("\nKey Observations (Demo 1):")
    print("• Direct-Mapped has 0% hit ratio due to conflict misses!")
    print("• Addresses 0, 16, 32 keep evicting each other (same cache line)")
    print(f"• Fully Associative achieves {fa_stats['hit_ratio']:.1f}% hit ratio - MUCH better!")
    print("• LRU allows blocks to coexist without conflicts")
    print("• Fully Associative has significantly lower memory traffic")
    print("="*70 + "\n")
    
    # Demonstration 2: Write-Through vs Write-Back
    print("\n" + "="*70)
    print(" Demo 2: Write-Through vs Write-Back Comparison ".center(70))
    print("="*70)
    print("\nCache Parameters: 16 bytes total, 4 bytes per block")
    print("Address Sequence: [0, 4, 8, 12, 0, 4, 8, 12]")
    print("Operations: All WRITE operations to highlight policy difference\n")
    
    addresses2 = [0, 4, 8, 12, 0, 4, 8, 12]
    
    # Write-Through Demo
    print("\n" + "#"*70)
    print(" PART 1: WRITE-THROUGH POLICY ".center(70, "#"))
    print("#"*70)
    
    wt_cache = DirectMappedCache(cache_size=16, block_size=4, write_policy='write-through')
    
    for addr in addresses2:
        wt_cache.access(addr, operation='write')
    
    wt_cache.display_cache()
    wt_cache.print_statistics()
    
    # Write-Back Demo
    print("\n" + "#"*70)
    print(" PART 2: WRITE-BACK POLICY ".center(70, "#"))
    print("#"*70)
    
    wb_cache = DirectMappedCache(cache_size=16, block_size=4, write_policy='write-back')
    
    for addr in addresses2:
        wb_cache.access(addr, operation='write')
    
    wb_cache.display_cache()
    wb_cache.print_statistics()
    
    # Comparison
    print("\n" + "="*70)
    print(" COMPARISON SUMMARY (Demo 2) ".center(70, "="))
    print("="*70)
    wt_stats = wt_cache.get_statistics()
    wb_stats = wb_cache.get_statistics()
    
    print(f"{'Metric':<30} {'Write-Through':<20} {'Write-Back':<20}")
    print("─"*70)
    print(f"{'Cache Hits':<30} {wt_stats['hits']:<20} {wb_stats['hits']:<20}")
    print(f"{'Cache Misses':<30} {wt_stats['misses']:<20} {wb_stats['misses']:<20}")
    print(f"{'Memory Reads':<30} {wt_stats['memory_reads']:<20} {wb_stats['memory_reads']:<20}")
    print(f"{'Memory Writes':<30} {wt_stats['memory_writes']:<20} {wb_stats['memory_writes']:<20}")
    wt_total = wt_stats['memory_reads'] + wt_stats['memory_writes']
    wb_total = wb_stats['memory_reads'] + wb_stats['memory_writes']
    print(f"{'Total Memory Traffic':<30} {wt_total:<20} {wb_total:<20}")
    
    write_reduction = ((wt_stats['memory_writes'] - wb_stats['memory_writes']) / wt_stats['memory_writes'] * 100) if wt_stats['memory_writes'] > 0 else 0
    print(f"\n{'Write Reduction':<30} {'—':<20} {write_reduction:.1f}%")
    print("="*70)
    
    print("\nKey Observations (Demo 2):")
    print(f"• Write-Through: {wt_stats['memory_writes']} memory writes (every write goes to memory)")
    print(f"• Write-Back: {wb_stats['memory_writes']} memory writes (only on first miss)")
    print(f"• Write-Back reduces memory writes by {write_reduction:.1f}%!")
    print("• Write-Back uses dirty bits to defer memory updates")
    print("• Write-Through ensures memory is always up-to-date")
    print("• Write-Back is more efficient but requires careful management")
    print("="*70 + "\n")


def interactive_mode():
    """Interactive mode for custom testing."""
    print("\n" + "="*70)
    print(" INTERACTIVE MODE ".center(70, "="))
    print("="*70)
    
    # Get cache configuration
    print("\nCache Configuration:")
    print("─"*70)
    
    while True:
        try:
            cache_size = int(input("Enter cache size in bytes (e.g., 16, 32, 64): "))
            if cache_size <= 0 or (cache_size & (cache_size - 1)) != 0:
                print("  ⚠ Cache size must be a positive power of 2!")
                continue
            break
        except ValueError:
            print("  ⚠ Please enter a valid integer!")
    
    while True:
        try:
            block_size = int(input("Enter block size in bytes (e.g., 4, 8, 16): "))
            if block_size <= 0 or (block_size & (block_size - 1)) != 0:
                print("  ⚠ Block size must be a positive power of 2!")
                continue
            if block_size > cache_size:
                print("  ⚠ Block size cannot exceed cache size!")
                continue
            break
        except ValueError:
            print("  ⚠ Please enter a valid integer!")
    
    print("\nCache Type:")
    print("  1. Direct-Mapped Cache")
    print("  2. Fully Associative Cache")
    
    while True:
        cache_type = input("Select cache type (1 or 2): ").strip()
        if cache_type in ['1', '2']:
            break
        print("  ⚠ Please enter 1 or 2!")
    
    print("\nWrite Policy:")
    print("  1. Write-Through")
    print("  2. Write-Back")
    
    while True:
        policy = input("Select write policy (1 or 2): ").strip()
        if policy in ['1', '2']:
            write_policy = 'write-through' if policy == '1' else 'write-back'
            break
        print("  ⚠ Please enter 1 or 2!")
    
    # Create cache
    if cache_type == '1':
        cache = DirectMappedCache(cache_size, block_size, write_policy)
    else:
        cache = FullyAssociativeCache(cache_size, block_size, write_policy)
    
    # Get address sequence
    print("\n" + "─"*70)
    print("Enter memory addresses to access:")
    print("  • Enter addresses as decimal (e.g., 0 16 32 48)")
    print("  • Or hex with 0x prefix (e.g., 0x0 0x10 0x20 0x30)")
    print("  • Separate multiple addresses with spaces")
    print("─"*70)
    
    while True:
        addr_input = input("\nAddresses: ").strip()
        if not addr_input:
            print("  ⚠ Please enter at least one address!")
            continue
        
        try:
            addresses = []
            for addr_str in addr_input.split():
                if addr_str.lower().startswith('0x'):
                    addresses.append(int(addr_str, 16))
                else:
                    addresses.append(int(addr_str))
            break
        except ValueError:
            print("  ⚠ Invalid address format! Use decimal or hex (0x prefix)")
    
    # Get operation sequence
    print("\n" + "─"*70)
    print("Enter operations for each address:")
    print("  • r = read, w = write")
    print("  • Separate with spaces (e.g., r w r r w)")
    print(f"  • You need {len(addresses)} operations")
    print("  • Or press Enter to default all to READ")
    print("─"*70)
    
    operations_input = input("\nOperations: ").strip()
    
    if operations_input:
        operations = []
        for op in operations_input.split():
            if op.lower() in ['r', 'read']:
                operations.append('read')
            elif op.lower() in ['w', 'write']:
                operations.append('write')
        
        # Pad with 'read' if not enough operations
        while len(operations) < len(addresses):
            operations.append('read')
    else:
        operations = ['read'] * len(addresses)
    
    # Execute simulation
    print("\n" + "="*70)
    print(" SIMULATION STARTED ".center(70, "="))
    print("="*70)
    
    for addr, operation in zip(addresses, operations):
        cache.access(addr, operation=operation)
    
    cache.display_cache()
    cache.print_statistics()


def main():
    """Main program entry point."""
    print_header()
    
    while True:
        print("\nMain Menu:")
        print("─"*70)
        print("  1. Run Sample Demonstration")
        print("  2. Interactive Mode (Custom Configuration)")
        print("  3. Exit")
        print("─"*70)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            run_sample_demo()
        elif choice == '2':
            interactive_mode()
        elif choice == '3':
            print("\n" + "="*70)
            print(" Thank you for using Cache Memory Simulator! ".center(70))
            print("="*70 + "\n")
            break
        else:
            print("  ⚠ Invalid choice! Please enter 1, 2, or 3.")
        
        if choice in ['1', '2']:
            input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    main()
