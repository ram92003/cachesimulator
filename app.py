"""
Flask Backend for Cache Simulator Web Interface
"""

from flask import Flask, render_template, jsonify, request
from src.cache_engine import DirectMappedCache, FullyAssociativeCache

app = Flask(__name__)

# Store active cache instance
active_cache = None


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/create_cache', methods=['POST'])
def create_cache():
    """Create a new cache with specified configuration."""
    global active_cache
    
    data = request.json
    cache_size = int(data.get('cache_size', 16))
    block_size = int(data.get('block_size', 4))
    cache_type = data.get('cache_type', 'direct-mapped')
    write_policy = data.get('write_policy', 'write-back')
    
    try:
        if cache_type == 'direct-mapped':
            active_cache = DirectMappedCache(cache_size, block_size, write_policy)
        else:
            active_cache = FullyAssociativeCache(cache_size, block_size, write_policy)
        
        return jsonify({
            'success': True,
            'cache_state': active_cache.get_cache_state()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/access', methods=['POST'])
def cache_access():
    """Process a cache access operation."""
    global active_cache
    
    if active_cache is None:
        return jsonify({
            'success': False,
            'error': 'No active cache. Create a cache first.'
        }), 400
    
    data = request.json
    address = int(data.get('address', 0))
    operation = data.get('operation', 'read')
    
    try:
        result = active_cache.access(address, operation)
        return jsonify({
            'success': True,
            **result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/get_state', methods=['GET'])
def get_state():
    """Get current cache state."""
    global active_cache
    
    if active_cache is None:
        return jsonify({
            'success': False,
            'error': 'No active cache'
        }), 400
    
    return jsonify({
        'success': True,
        'cache_state': active_cache.get_cache_state()
    })


@app.route('/api/reset', methods=['POST'])
def reset_cache():
    """Reset the cache."""
    global active_cache
    
    if active_cache is None:
        return jsonify({
            'success': False,
            'error': 'No active cache'
        }), 400
    
    # Recreate cache with same parameters
    cache_size = active_cache.cache_size
    block_size = active_cache.block_size
    cache_type = active_cache.cache_type
    write_policy = active_cache.write_policy
    
    if cache_type == 'direct-mapped':
        active_cache = DirectMappedCache(cache_size, block_size, write_policy)
    else:
        active_cache = FullyAssociativeCache(cache_size, block_size, write_policy)
    
    return jsonify({
        'success': True,
        'cache_state': active_cache.get_cache_state()
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
