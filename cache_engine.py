"""
Cache Memory Simulation Engine
Core logic for Direct-Mapped and Fully Associative cache simulation
"""

import math
from collections import OrderedDict


class CacheBlock:
    """Represents a single cache block/line with metadata."""
    
    def __init__(self):
        self.valid = 0
        self.tag = None
        self.data = None
        self.dirty = 0
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'valid': self.valid,
            'tag': self.tag,
            'data': self.data,
            'dirty': self.dirty
        }


class CacheSimulator:
    """Base class for cache simulation."""
    
    def __init__(self, cache_size, block_size, write_policy='write-through'):
        self.cache_size = cache_size
        self.block_size = block_size
        self.num_blocks = cache_size // block_size
        self.write_policy = write_policy
        self.offset_bits = int(math.log2(block_size))
        
        # Statistics
        self.total_accesses = 0
        self.hits = 0
        self.misses = 0
        self.memory_reads = 0
        self.memory_writes = 0
        
        # Operation log
        self.operation_log = []
    
    def get_statistics(self):
        """Return comprehensive statistics."""
        hit_ratio = (self.hits / self.total_accesses * 100) if self.total_accesses > 0 else 0
        miss_ratio = (self.misses / self.total_accesses * 100) if self.total_accesses > 0 else 0
        
        return {
            'total_accesses': self.total_accesses,
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': round(hit_ratio, 2),
            'miss_ratio': round(miss_ratio, 2),
            'memory_reads': self.memory_reads,
            'memory_writes': self.memory_writes,
            'total_memory_traffic': self.memory_reads + self.memory_writes
        }
    
    def log_operation(self, message, level='info'):
        """Add to operation log."""
        self.operation_log.append({'message': message, 'level': level})


class DirectMappedCache(CacheSimulator):
    """Direct-Mapped Cache Implementation."""
    
    def __init__(self, cache_size, block_size, write_policy='write-through'):
        super().__init__(cache_size, block_size, write_policy)
        
        self.index_bits = int(math.log2(self.num_blocks))
        self.tag_bits = 32 - self.index_bits - self.offset_bits
        self.cache = [CacheBlock() for _ in range(self.num_blocks)]
        self.cache_type = 'direct-mapped'
    
    def decompose_address(self, address):
        """Decompose address into tag, index, offset."""
        offset_mask = (1 << self.offset_bits) - 1
        offset = address & offset_mask
        
        index_mask = (1 << self.index_bits) - 1
        index = (address >> self.offset_bits) & index_mask
        
        tag = address >> (self.offset_bits + self.index_bits)
        
        return tag, index, offset
    
    def access(self, address, operation='read', data=None):
        """
        Simulate cache access and return detailed step-by-step information.
        """
        self.total_accesses += 1
        tag, index, offset = self.decompose_address(address)
        
        # Initialize response
        response = {
            'access_number': self.total_accesses,
            'address': address,
            'operation': operation,
            'decomposition': {
                'tag': tag,
                'index': index,
                'offset': offset
            },
            'steps': [],
            'hit': False,
            'eviction': False,
            'dirty_writeback': False,
            'affected_line': index,
            'cache_state': None,
            'statistics': None
        }
        
        cache_line = self.cache[index]
        
        # Step 1: Fetch
        response['steps'].append({
            'name': 'Fetch',
            'description': f'Accessing cache line {index}',
            'active': True
        })
        
        # Step 2: Compare Tag
        if cache_line.valid == 1 and cache_line.tag == tag:
            # CACHE HIT
            self.hits += 1
            response['hit'] = True
            response['steps'].append({
                'name': 'Compare Tag',
                'description': f'Tag match! ({tag} == {cache_line.tag})',
                'active': True
            })
            
            # Step 3: Hit Decision
            response['steps'].append({
                'name': 'Hit/Miss',
                'description': '✓ CACHE HIT - Data found in cache!',
                'active': True
            })
            
            if operation == 'write':
                self._handle_write_hit(index, address, data, response)
            
        else:
            # CACHE MISS
            self.misses += 1
            response['hit'] = False
            
            if cache_line.valid == 1:
                response['steps'].append({
                    'name': 'Compare Tag',
                    'description': f'Tag mismatch ({tag} != {cache_line.tag})',
                    'active': True
                })
                response['eviction'] = True
                
                if self.write_policy == 'write-back' and cache_line.dirty == 1:
                    self.memory_writes += 1
                    response['dirty_writeback'] = True
            else:
                response['steps'].append({
                    'name': 'Compare Tag',
                    'description': 'Cache line empty (invalid)',
                    'active': True
                })
            
            # Step 3: Miss Decision
            response['steps'].append({
                'name': 'Hit/Miss',
                'description': '✗ CACHE MISS - Must fetch from memory',
                'active': True
            })
            
            self._fetch_from_memory(index, tag, address, operation, data, response)
        
        # Step 4: Update Cache
        response['steps'].append({
            'name': 'Update Cache',
            'description': 'Cache line updated',
            'active': True
        })
        
        # Get final cache state
        response['cache_state'] = [block.to_dict() for block in self.cache]
        response['statistics'] = self.get_statistics()
        
        return response
    
    def _handle_write_hit(self, index, address, data, response):
        """Handle write operation on cache hit."""
        cache_line = self.cache[index]
        
        if self.write_policy == 'write-through':
            cache_line.data = address if data is None else data
            self.memory_writes += 1
            cache_line.dirty = 0
            response['steps'].append({
                'name': 'Write',
                'description': 'Write-through: updated cache AND memory',
                'active': True
            })
        else:
            cache_line.data = address if data is None else data
            cache_line.dirty = 1
            response['steps'].append({
                'name': 'Write',
                'description': 'Write-back: updated cache only (dirty bit set)',
                'active': True
            })
    
    def _fetch_from_memory(self, index, tag, address, operation, data, response):
        """Fetch block from memory and update cache."""
        cache_line = self.cache[index]
        
        self.memory_reads += 1
        response['steps'].append({
            'name': 'Memory Fetch',
            'description': f'Fetching block from memory (reads: {self.memory_reads})',
            'active': True
        })
        
        cache_line.valid = 1
        cache_line.tag = tag
        cache_line.data = address if data is None else data
        
        if operation == 'write':
            if self.write_policy == 'write-through':
                cache_line.dirty = 0
                self.memory_writes += 1
            else:
                cache_line.dirty = 1
        else:
            cache_line.dirty = 0
    
    def get_cache_state(self):
        """Return current cache state."""
        return {
            'type': self.cache_type,
            'size': self.cache_size,
            'block_size': self.block_size,
            'num_blocks': self.num_blocks,
            'write_policy': self.write_policy,
            'bits': {
                'tag': self.tag_bits,
                'index': self.index_bits,
                'offset': self.offset_bits
            },
            'lines': [block.to_dict() for block in self.cache],
            'statistics': self.get_statistics()
        }


class FullyAssociativeCache(CacheSimulator):
    """Fully Associative Cache Implementation with LRU."""
    
    def __init__(self, cache_size, block_size, write_policy='write-through'):
        super().__init__(cache_size, block_size, write_policy)
        
        self.tag_bits = 32 - self.offset_bits
        self.cache = OrderedDict()
        for i in range(self.num_blocks):
            self.cache[i] = CacheBlock()
        self.cache_type = 'fully-associative'
    
    def decompose_address(self, address):
        """Decompose address into tag and offset."""
        offset_mask = (1 << self.offset_bits) - 1
        offset = address & offset_mask
        tag = address >> self.offset_bits
        return tag, offset
    
    def _find_block(self, tag):
        """Search for matching tag."""
        for line_num, block in self.cache.items():
            if block.valid == 1 and block.tag == tag:
                return line_num
        return None
    
    def _find_empty_line(self):
        """Find empty cache line."""
        for line_num, block in self.cache.items():
            if block.valid == 0:
                return line_num
        return None
    
    def _evict_lru(self):
        """Evict least recently used line."""
        return next(iter(self.cache))
    
    def _update_lru(self, line_num):
        """Update LRU order."""
        self.cache.move_to_end(line_num)
    
    def access(self, address, operation='read', data=None):
        """Simulate cache access."""
        self.total_accesses += 1
        tag, offset = self.decompose_address(address)
        
        response = {
            'access_number': self.total_accesses,
            'address': address,
            'operation': operation,
            'decomposition': {
                'tag': tag,
                'offset': offset
            },
            'steps': [],
            'hit': False,
            'eviction': False,
            'dirty_writeback': False,
            'affected_line': None,
            'cache_state': None,
            'statistics': None
        }
        
        # Step 1: Search all lines
        response['steps'].append({
            'name': 'Search',
            'description': f'Searching {self.num_blocks} lines for tag {tag}',
            'active': True
        })
        
        hit_line = self._find_block(tag)
        
        if hit_line is not None:
            # CACHE HIT
            self.hits += 1
            response['hit'] = True
            response['affected_line'] = hit_line
            
            response['steps'].append({
                'name': 'Compare Tag',
                'description': f'Tag found in line {hit_line}!',
                'active': True
            })
            
            # Step 3: Hit Decision
            response['steps'].append({
                'name': 'Hit/Miss',
                'description': '✓ CACHE HIT - Data found in cache!',
                'active': True
            })
            
            self._update_lru(hit_line)
            
            if operation == 'write':
                self._handle_write_hit(hit_line, address, data, response)
        else:
            # CACHE MISS
            self.misses += 1
            response['hit'] = False
            
            response['steps'].append({
                'name': 'Compare Tag',
                'description': 'Tag not found in any line',
                'active': True
            })
            
            # Step 3: Miss Decision
            response['steps'].append({
                'name': 'Hit/Miss',
                'description': '✗ CACHE MISS - Must fetch from memory',
                'active': True
            })
            
            empty_line = self._find_empty_line()
            
            if empty_line is not None:
                target_line = empty_line
            else:
                target_line = self._evict_lru()
                evicted_block = self.cache[target_line]
                response['eviction'] = True
                
                if self.write_policy == 'write-back' and evicted_block.dirty == 1:
                    self.memory_writes += 1
                    response['dirty_writeback'] = True
            
            response['affected_line'] = target_line
            self._fetch_from_memory(target_line, tag, address, operation, data, response)
            self._update_lru(target_line)
        
        response['steps'].append({
            'name': 'Update Cache',
            'description': 'Cache updated',
            'active': True
        })
        
        response['cache_state'] = [block.to_dict() for line_num, block in self.cache.items()]
        response['statistics'] = self.get_statistics()
        
        return response
    
    def _handle_write_hit(self, line_num, address, data, response):
        """Handle write hit."""
        cache_line = self.cache[line_num]
        
        if self.write_policy == 'write-through':
            cache_line.data = address if data is None else data
            self.memory_writes += 1
            cache_line.dirty = 0
            response['steps'].append({
                'name': 'Write',
                'description': 'Write-through executed',
                'active': True
            })
        else:
            cache_line.data = address if data is None else data
            cache_line.dirty = 1
            response['steps'].append({
                'name': 'Write',
                'description': 'Write-back: dirty bit set',
                'active': True
            })
    
    def _fetch_from_memory(self, line_num, tag, address, operation, data, response):
        """Fetch from memory."""
        cache_line = self.cache[line_num]
        
        self.memory_reads += 1
        response['steps'].append({
            'name': 'Memory Fetch',
            'description': f'Fetching from memory (reads: {self.memory_reads})',
            'active': True
        })
        
        cache_line.valid = 1
        cache_line.tag = tag
        cache_line.data = address if data is None else data
        
        if operation == 'write':
            if self.write_policy == 'write-through':
                cache_line.dirty = 0
                self.memory_writes += 1
            else:
                cache_line.dirty = 1
        else:
            cache_line.dirty = 0
    
    def get_cache_state(self):
        """Return current cache state."""
        return {
            'type': self.cache_type,
            'size': self.cache_size,
            'block_size': self.block_size,
            'num_blocks': self.num_blocks,
            'write_policy': self.write_policy,
            'bits': {
                'tag': self.tag_bits,
                'offset': self.offset_bits
            },
            'lines': [block.to_dict() for line_num, block in self.cache.items()],
            'statistics': self.get_statistics()
        }
