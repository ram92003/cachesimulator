// Interactive Cache Simulator JavaScript
// Handles all UI interactions, animations, and API communication

class CacheSimulator {
    constructor() {
        this.cacheState = null;
        this.soundEnabled = false;
        this.logCounter = 0;
        
        // Sound effects (Base64 encoded simple beeps - can be replaced with actual sound files)
        this.sounds = {
            hit: this.createBeep(800, 0.1),
            miss: this.createBeep(200, 0.2)
        };
        
        this.initializeElements();
        this.attachEventListeners();
        this.setupCollapsiblePanels();
    }
    
    initializeElements() {
        // Configuration elements
        this.cacheSizeSelect = document.getElementById('cache-size');
        this.blockSizeSelect = document.getElementById('block-size');
        this.cacheTypeSelect = document.getElementById('cache-type');
        this.writePolicySelect = document.getElementById('write-policy');
        this.createCacheBtn = document.getElementById('create-cache-btn');
        
        // Operation elements
        this.memoryAddressInput = document.getElementById('memory-address');
        this.operationTypeSelect = document.getElementById('operation-type');
        this.executeBtn = document.getElementById('execute-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.soundToggle = document.getElementById('sound-enabled');
        
        // Display elements
        this.cacheTableContainer = document.getElementById('cache-table-container');
        this.cacheInfo = document.getElementById('cache-info');
        this.logContainer = document.getElementById('log-container');
        this.progressIndicator = document.getElementById('progress-indicator');
        this.clearLogBtn = document.getElementById('clear-log-btn');
        
        // Statistics elements
        this.statTotal = document.getElementById('stat-total');
        this.statHits = document.getElementById('stat-hits');
        this.statMisses = document.getElementById('stat-misses');
        this.statHitRatio = document.getElementById('stat-hit-ratio');
        this.statMemReads = document.getElementById('stat-mem-reads');
        this.statMemWrites = document.getElementById('stat-mem-writes');
    }
    
    attachEventListeners() {
        this.createCacheBtn.addEventListener('click', () => this.createCache());
        this.executeBtn.addEventListener('click', () => this.executeOperation());
        this.resetBtn.addEventListener('click', () => this.resetCache());
        this.clearLogBtn.addEventListener('click', () => this.clearLog());
        this.soundToggle.addEventListener('change', (e) => {
            this.soundEnabled = e.target.checked;
        });
        
        // Enter key support for address input
        this.memoryAddressInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.executeBtn.disabled) {
                this.executeOperation();
            }
        });
    }
    
    setupCollapsiblePanels() {
        const collapsibleHeaders = document.querySelectorAll('.panel-header.collapsible');
        
        collapsibleHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const targetId = header.getAttribute('data-target');
                const target = document.getElementById(targetId);
                
                target.classList.toggle('collapsed');
                header.classList.toggle('collapsed');
            });
        });
    }
    
    async createCache() {
        const config = {
            cache_size: parseInt(this.cacheSizeSelect.value),
            block_size: parseInt(this.blockSizeSelect.value),
            cache_type: this.cacheTypeSelect.value,
            write_policy: this.writePolicySelect.value
        };
        
        this.showLoading(this.createCacheBtn);
        
        try {
            const response = await fetch('/api/create_cache', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.cacheState = data.cache_state;
                this.renderCache();
                this.updateStatistics(data.cache_state.statistics);
                this.executeBtn.disabled = false;
                this.resetBtn.disabled = false;
                this.addLog('Cache created successfully!', 'success');
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Failed to create cache: ' + error.message);
        } finally {
            this.hideLoading(this.createCacheBtn);
        }
    }
    
    async executeOperation() {
        const address = parseInt(this.memoryAddressInput.value);
        const operation = this.operationTypeSelect.value;
        
        if (isNaN(address) || address < 0) {
            this.showError('Please enter a valid memory address');
            return;
        }
        
        this.showLoading(this.executeBtn);
        this.showProgressIndicator();
        
        try {
            const response = await fetch('/api/access', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    address: address,
                    operation: operation
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                await this.animateOperation(data);
                this.cacheState = { ...this.cacheState, lines: data.cache_state, statistics: data.statistics };
                this.renderCache();
                this.updateStatistics(data.statistics);
                this.logOperation(data);
                
                // Play sound effect
                if (this.soundEnabled) {
                    this.playSound(data.hit ? 'hit' : 'miss');
                }
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Failed to execute operation: ' + error.message);
        } finally {
            this.hideLoading(this.executeBtn);
            setTimeout(() => this.hideProgressIndicator(), 2000);
        }
    }
    
    async animateOperation(data) {
        // Animate progress steps - map backend steps to frontend indicator
        if (data.steps && data.steps.length > 0) {
            const stepElements = document.querySelectorAll('.progress-step');
            const stepMapping = {
                'Fetch': 0,
                'Search': 0,
                'Compare Tag': 1,
                'Compare': 1,
                'Hit/Miss': 2,
                'Memory Fetch': 2, // Keep on Hit/Miss step during memory fetch
                'Write': 3,
                'LRU Eviction': 2, // Keep on Hit/Miss during eviction
                'Update Cache': 3,
                'Update': 3
            };
            
            for (let i = 0; i < data.steps.length; i++) {
                const backendStepName = data.steps[i].name;
                const frontendStepIndex = stepMapping[backendStepName] || i;
                
                // Only activate steps that exist in the frontend
                if (frontendStepIndex < stepElements.length) {
                    stepElements.forEach(el => el.classList.remove('active'));
                    stepElements[frontendStepIndex].classList.add('active');
                    await this.delay(400);
                }
            }
        }
        
        // Highlight affected cache line
        if (data.affected_line !== null && data.affected_line !== undefined) {
            await this.delay(300);
            const row = document.querySelector(`tr[data-line="${data.affected_line}"]`);
            
            if (row) {
                row.classList.add(data.hit ? 'hit' : 'miss');
                await this.delay(800);
                row.classList.remove('hit', 'miss');
                row.classList.add('loading');
                await this.delay(800);
                row.classList.remove('loading');
            }
        }
    }
    
    renderCache() {
        if (!this.cacheState || !this.cacheState.lines) {
            return;
        }
        
        // Update cache info
        const bits = this.cacheState.bits;
        let bitInfo = `<strong>Address Bits:</strong> `;
        
        if (this.cacheState.type === 'direct-mapped') {
            bitInfo += `Tag: ${bits.tag} | Index: ${bits.index} | Offset: ${bits.offset}`;
        } else {
            bitInfo += `Tag: ${bits.tag} | Offset: ${bits.offset} (No Index - Fully Associative)`;
        }
        
        bitInfo += ` | <strong>Policy:</strong> ${this.cacheState.write_policy}`;
        this.cacheInfo.innerHTML = bitInfo;
        
        // Build cache table
        let tableHTML = `
            <table class="cache-table">
                <thead>
                    <tr>
                        <th>Line #</th>
                        <th>Valid Bit</th>
                        <th>Tag</th>
                        <th>Dirty Bit</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        this.cacheState.lines.forEach((line, index) => {
            const validClass = line.valid === 1 ? 'field-valid' : 'field-invalid';
            const dirtyClass = line.dirty === 1 ? 'field-dirty' : 'field-invalid';
            const tagValue = line.tag !== null ? `0x${line.tag.toString(16).toUpperCase().padStart(4, '0')}` : '-';
            const dataValue = line.data !== null ? `0x${line.data.toString(16).toUpperCase().padStart(8, '0')}` : '-';
            
            tableHTML += `
                <tr data-line="${index}">
                    <td><strong>${index}</strong></td>
                    <td>
                        <span class="cache-field ${validClass}" data-tooltip="Valid bit indicates if this cache line contains valid data">
                            ${line.valid}
                        </span>
                    </td>
                    <td>
                        <span class="cache-field field-tag" data-tooltip="Tag identifies which memory block is stored in this line">
                            ${tagValue}
                        </span>
                    </td>
                    <td>
                        <span class="cache-field ${dirtyClass}" data-tooltip="Dirty bit shows if data has been modified (write-back policy)">
                            ${line.dirty}
                        </span>
                    </td>
                    <td>
                        <span class="cache-field field-data" data-tooltip="Data stored in this cache block">
                            ${dataValue}
                        </span>
                    </td>
                </tr>
            `;
        });
        
        tableHTML += `
                </tbody>
            </table>
        `;
        
        this.cacheTableContainer.innerHTML = tableHTML;
        
        // Add tooltips to cache fields
        this.addFieldTooltips();
    }
    
    addFieldTooltips() {
        const fields = document.querySelectorAll('.cache-field[data-tooltip]');
        
        fields.forEach(field => {
            field.addEventListener('mouseenter', (e) => {
                const tooltip = document.createElement('div');
                tooltip.className = 'field-tooltip';
                tooltip.textContent = e.target.getAttribute('data-tooltip');
                tooltip.style.position = 'absolute';
                tooltip.style.background = '#1e293b';
                tooltip.style.color = 'white';
                tooltip.style.padding = '8px 12px';
                tooltip.style.borderRadius = '8px';
                tooltip.style.fontSize = '0.85rem';
                tooltip.style.zIndex = '1000';
                tooltip.style.pointerEvents = 'none';
                tooltip.style.maxWidth = '200px';
                tooltip.style.boxShadow = '0 10px 15px -3px rgb(0 0 0 / 0.1)';
                
                document.body.appendChild(tooltip);
                
                const rect = e.target.getBoundingClientRect();
                tooltip.style.left = rect.left + 'px';
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
                
                e.target.tooltipElement = tooltip;
            });
            
            field.addEventListener('mouseleave', (e) => {
                if (e.target.tooltipElement) {
                    e.target.tooltipElement.remove();
                    e.target.tooltipElement = null;
                }
            });
        });
    }
    
    updateStatistics(stats) {
        this.animateValue(this.statTotal, stats.total_accesses);
        this.animateValue(this.statHits, stats.hits);
        this.animateValue(this.statMisses, stats.misses);
        this.statHitRatio.textContent = stats.hit_ratio + '%';
        this.animateValue(this.statMemReads, stats.memory_reads);
        this.animateValue(this.statMemWrites, stats.memory_writes);
    }
    
    animateValue(element, value) {
        element.style.animation = 'none';
        setTimeout(() => {
            element.textContent = value;
            element.style.animation = 'countUp 0.5s ease-out';
        }, 10);
    }
    
    logOperation(data) {
        const timestamp = new Date().toLocaleTimeString();
        const hitStatus = data.hit ? 'HIT' : 'MISS';
        const hitClass = data.hit ? 'hit' : 'miss';
        const operation = data.operation.toUpperCase();
        
        const decomp = data.decomposition;
        let decompStr = '';
        if (decomp.index !== undefined) {
            decompStr = `Tag: 0x${decomp.tag.toString(16)} | Index: ${decomp.index} | Offset: ${decomp.offset}`;
        } else {
            decompStr = `Tag: 0x${decomp.tag.toString(16)} | Offset: ${decomp.offset}`;
        }
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry latest ${hitClass}`;
        logEntry.innerHTML = `
            <div class="log-time">${timestamp} - Access #${data.access_number}</div>
            <div><strong>${operation}</strong> 0x${data.address.toString(16).toUpperCase().padStart(8, '0')} → <strong>${hitStatus}</strong></div>
            <div style="font-size: 0.85rem; margin-top: 4px;">${decompStr}</div>
            ${data.eviction ? '<div style="color: #f59e0b; margin-top: 4px;"><i class="fas fa-exclamation-triangle"></i> Eviction occurred</div>' : ''}
            ${data.dirty_writeback ? '<div style="color: #ef4444; margin-top: 4px;"><i class="fas fa-database"></i> Dirty block written back to memory</div>' : ''}
        `;
        
        // Remove 'latest' class from previous entries
        document.querySelectorAll('.log-entry.latest').forEach(entry => {
            entry.classList.remove('latest');
        });
        
        this.logContainer.insertBefore(logEntry, this.logContainer.firstChild);
        
        // Auto-scroll to top
        this.logContainer.scrollTop = 0;
        
        this.logCounter++;
    }
    
    addLog(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry latest`;
        logEntry.innerHTML = `
            <div class="log-time">${timestamp}</div>
            <div>${message}</div>
        `;
        
        this.logContainer.insertBefore(logEntry, this.logContainer.firstChild);
        this.logContainer.scrollTop = 0;
    }
    
    clearLog() {
        this.logContainer.innerHTML = '<p class="placeholder-text"><i class="fas fa-info-circle"></i> Operation logs will appear here</p>';
        this.logCounter = 0;
    }
    
    async resetCache() {
        if (!confirm('Are you sure you want to reset the cache? All data will be cleared.')) {
            return;
        }
        
        this.showLoading(this.resetBtn);
        
        try {
            const response = await fetch('/api/reset', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.cacheState = data.cache_state;
                this.renderCache();
                this.updateStatistics(data.cache_state.statistics);
                this.clearLog();
                this.addLog('Cache reset successfully!', 'success');
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Failed to reset cache: ' + error.message);
        } finally {
            this.hideLoading(this.resetBtn);
        }
    }
    
    showProgressIndicator() {
        this.progressIndicator.style.display = 'block';
    }
    
    hideProgressIndicator() {
        this.progressIndicator.style.display = 'none';
        document.querySelectorAll('.progress-step').forEach(el => el.classList.remove('active'));
    }
    
    showLoading(button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    }
    
    hideLoading(button) {
        button.disabled = false;
        // Restore original button content
        if (button === this.createCacheBtn) {
            button.innerHTML = '<i class="fas fa-play"></i> Create Cache';
        } else if (button === this.executeBtn) {
            button.innerHTML = '<i class="fas fa-bolt"></i> Execute Operation';
        } else if (button === this.resetBtn) {
            button.innerHTML = '<i class="fas fa-redo"></i> Reset Cache';
        }
    }
    
    showError(message) {
        const modal = document.getElementById('result-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        
        modalTitle.textContent = 'Error';
        modalBody.innerHTML = `<p style="color: var(--danger-color);"><i class="fas fa-exclamation-circle"></i> ${message}</p>`;
        modal.classList.add('show');
        
        // Close modal on click outside or close button
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.onclick = () => modal.classList.remove('show');
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        };
    }
    
    // Simple beep sound generation using Web Audio API
    createBeep(frequency, duration) {
        return () => {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration);
        };
    }
    
    playSound(soundType) {
        if (this.sounds[soundType]) {
            try {
                this.sounds[soundType]();
            } catch (error) {
                console.log('Sound playback failed:', error);
            }
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the simulator when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.simulator = new CacheSimulator();
});
