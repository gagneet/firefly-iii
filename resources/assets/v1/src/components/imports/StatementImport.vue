<template>
  <div class="statement-import">
    <div class="box box-primary">
      <div class="box-header with-border">
        <h3 class="box-title">
          <i class="fa fa-file-pdf-o"></i>
          Import Bank Statement (PDF)
        </h3>
      </div>

      <div class="box-body">
        <!-- Bank Selection -->
        <div class="form-group">
          <label for="bank-select">Select Your Bank</label>
          <select
            id="bank-select"
            v-model="selectedBank"
            class="form-control"
            :disabled="importing"
          >
            <option value="">-- Choose a bank --</option>
            <option
              v-for="bank in banks"
              :key="bank.value"
              :value="bank.value"
            >
              {{ bank.label }}
            </option>
          </select>
          <p class="help-block" v-if="selectedBankInfo">
            {{ selectedBankInfo.description }}
          </p>
        </div>

        <!-- File Upload -->
        <div class="form-group">
          <label for="file-upload">PDF Statement</label>
          <input
            id="file-upload"
            type="file"
            accept=".pdf"
            @change="onFileChange"
            class="form-control"
            :disabled="!selectedBank || importing"
            ref="fileInput"
          />
          <p class="help-block">
            Maximum file size: 10MB. Only PDF files are accepted.
          </p>
        </div>

        <!-- Options -->
        <div class="form-group">
          <label>Import Options</label>
          <div class="checkbox">
            <label>
              <input
                type="checkbox"
                v-model="detectDuplicates"
                :disabled="importing"
              />
              Detect and skip duplicate transactions
            </label>
          </div>
          <div class="checkbox">
            <label>
              <input
                type="checkbox"
                v-model="detectTransfers"
                :disabled="importing"
              />
              Detect transfers between your accounts
            </label>
          </div>
        </div>

        <!-- File Info -->
        <div v-if="file" class="alert alert-info">
          <strong>Selected file:</strong> {{ file.name }}
          ({{ formatFileSize(file.size) }})
        </div>

        <!-- Progress -->
        <div v-if="importing" class="progress">
          <div
            class="progress-bar progress-bar-striped active"
            role="progressbar"
            style="width: 100%"
          >
            <span>Processing statement...</span>
          </div>
        </div>

        <!-- Results -->
        <div v-if="importResult" class="alert" :class="resultAlertClass">
          <h4>
            <i class="fa" :class="resultIconClass"></i>
            {{ importResult.message }}
          </h4>
          <div v-if="importResult.data" class="import-stats">
            <table class="table table-condensed">
              <tr>
                <td><strong>Total transactions:</strong></td>
                <td>{{ importResult.data.total }}</td>
              </tr>
              <tr v-if="importResult.data.created > 0" class="success">
                <td><strong>Successfully imported:</strong></td>
                <td>{{ importResult.data.created }}</td>
              </tr>
              <tr v-if="importResult.data.transfers > 0" class="info">
                <td><strong>Transfers detected:</strong></td>
                <td>{{ importResult.data.transfers }}</td>
              </tr>
              <tr v-if="importResult.data.duplicates > 0" class="warning">
                <td><strong>Duplicates skipped:</strong></td>
                <td>{{ importResult.data.duplicates }}</td>
              </tr>
              <tr v-if="importResult.data.errors > 0" class="danger">
                <td><strong>Errors:</strong></td>
                <td>{{ importResult.data.errors }}</td>
              </tr>
            </table>

            <!-- Detailed Error List -->
            <div v-if="importResult.data.error_details && importResult.data.error_details.length > 0" class="error-details">
              <h5><i class="fa fa-exclamation-triangle"></i> Error Details:</h5>
              <ul class="error-list">
                <li v-for="(error, index) in importResult.data.error_details" :key="index">
                  {{ error }}
                </li>
              </ul>
            </div>

            <!-- CSV Download Option -->
            <div v-if="importResult.success" class="download-section">
              <hr>
              <button class="btn btn-info" @click="downloadCSV">
                <i class="fa fa-download"></i>
                Download as CSV
              </button>
              <p class="help-block">
                Download the processed transactions as a CSV file for your records
              </p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="alert alert-danger">
          <h4><i class="fa fa-exclamation-triangle"></i> Error</h4>
          <p>{{ errorMessage }}</p>
        </div>
      </div>

      <div class="box-footer">
        <button
          type="button"
          class="btn btn-primary"
          @click="uploadStatement"
          :disabled="!canUpload"
        >
          <i class="fa fa-upload"></i>
          Import Statement
        </button>

        <button
          type="button"
          class="btn btn-default"
          @click="reset"
          :disabled="importing"
        >
          <i class="fa fa-refresh"></i>
          Reset
        </button>
      </div>
    </div>

    <!-- Help Box -->
    <div class="box box-info collapsed-box">
      <div class="box-header with-border">
        <h3 class="box-title">
          <i class="fa fa-question-circle"></i>
          Help & Information
        </h3>
        <div class="box-tools pull-right">
          <button type="button" class="btn btn-box-tool" data-widget="collapse">
            <i class="fa fa-plus"></i>
          </button>
        </div>
      </div>
      <div class="box-body">
        <h4>Supported Banks</h4>
        <ul>
          <li><strong>American Express:</strong> Credit card statements</li>
          <li><strong>ING Orange Everyday:</strong> Transaction account statements</li>
          <li><strong>ING Savings Maximiser:</strong> Savings account statements</li>
          <li><strong>uBank Spend:</strong> Transaction account statements</li>
          <li><strong>Commonwealth Bank:</strong> Account statements</li>
        </ul>

        <h4>How It Works</h4>
        <ol>
          <li>Select your bank from the dropdown</li>
          <li>Choose your PDF statement file</li>
          <li>Click "Import Statement"</li>
          <li>The system will:
            <ul>
              <li>Extract all transactions from the PDF</li>
              <li>Detect and skip duplicates</li>
              <li>Identify transfers between your accounts</li>
              <li>Automatically categorize transactions</li>
              <li>Create accounts if they don't exist</li>
            </ul>
          </li>
        </ol>

        <h4>Duplicate Detection</h4>
        <p>
          The system automatically detects:
        </p>
        <ul>
          <li>Exact duplicate transactions (same transaction appearing multiple times)</li>
          <li>Transfers between your own accounts (to avoid double-counting)</li>
        </ul>

        <h4>Tips</h4>
        <ul>
          <li>Download statements as PDF from your bank's website</li>
          <li>Import statements in chronological order</li>
          <li>Check the results after import to verify accuracy</li>
          <li>The system will skip transactions that already exist</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'StatementImport',

  data() {
    return {
      banks: [],
      selectedBank: '',
      file: null,
      detectDuplicates: true,
      detectTransfers: true,
      importing: false,
      importResult: null,
      errorMessage: null
    };
  },

  computed: {
    selectedBankInfo() {
      return this.banks.find(b => b.value === this.selectedBank);
    },

    canUpload() {
      return this.selectedBank && this.file && !this.importing;
    },

    resultAlertClass() {
      if (!this.importResult) return '';
      return this.importResult.success ? 'alert-success' : 'alert-danger';
    },

    resultIconClass() {
      if (!this.importResult) return '';
      return this.importResult.success ? 'fa-check-circle' : 'fa-exclamation-circle';
    }
  },

  mounted() {
    this.loadBanks();
  },

  methods: {
    async loadBanks() {
      try {
        const response = await axios.get('/api/v1/statement-import/banks');
        this.banks = response.data.data;
      } catch (error) {
        console.error('Error loading banks:', error);
        this.errorMessage = 'Failed to load supported banks';
      }
    },

    async downloadCSV() {
      if (!this.importResult || !this.importResult.data) return;

      // Generate CSV from import result data
      const csvData = this.generateCSV(this.importResult.data);
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `firefly_import_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    },

    generateCSV(data) {
      const rows = [
        ['Date', 'Description', 'Amount', 'Category', 'Account', 'Type', 'Status']
      ];

      // Add transaction data (this would come from the API response)
      // For now, just create a summary row
      rows.push([
        new Date().toISOString().split('T')[0],
        'Import Summary',
        '',
        '',
        '',
        '',
        `${data.created} created, ${data.duplicates} skipped`
      ]);

      return rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    },

    onFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        // Validate file type
        if (file.type !== 'application/pdf') {
          this.errorMessage = 'Please select a PDF file';
          this.$refs.fileInput.value = '';
          return;
        }

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
          this.errorMessage = 'File size must be less than 10MB';
          this.$refs.fileInput.value = '';
          return;
        }

        this.file = file;
        this.errorMessage = null;
        this.importResult = null;
      }
    },

    async uploadStatement() {
      if (!this.canUpload) return;

      this.importing = true;
      this.importResult = null;
      this.errorMessage = null;

      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('bank_type', this.selectedBank);
      formData.append('detect_duplicates', this.detectDuplicates ? '1' : '0');
      formData.append('detect_transfers', this.detectTransfers ? '1' : '0');

      try {
        const response = await axios.post('/api/v1/statement-import/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        this.importResult = response.data;

      } catch (error) {
        console.error('Upload error:', error);

        if (error.response) {
          this.importResult = {
            success: false,
            message: error.response.data.message || 'Import failed'
          };
        } else {
          this.errorMessage = 'Network error. Please try again.';
        }
      } finally {
        this.importing = false;
      }
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    },

    reset() {
      this.selectedBank = '';
      this.file = null;
      this.importResult = null;
      this.errorMessage = null;
      this.detectDuplicates = true;
      this.detectTransfers = true;
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    }
  }
};
</script>

<style scoped>
.statement-import {
  margin: 20px 0;
}

.import-stats {
  margin-top: 15px;
}

.import-stats table {
  background: transparent;
  margin-bottom: 0;
}

.import-stats td {
  border: none !important;
  padding: 5px 10px;
}

.progress {
  margin-top: 20px;
}

.alert h4 {
  margin-top: 0;
}

.error-details {
  margin-top: 15px;
  padding: 10px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
}

.error-details h5 {
  margin-top: 0;
  color: #856404;
}

.error-list {
  margin-bottom: 0;
  padding-left: 20px;
}

.error-list li {
  color: #721c24;
  margin-bottom: 5px;
}

.download-section {
  margin-top: 15px;
}

.download-section hr {
  margin: 15px 0;
}

.download-section .btn {
  margin-bottom: 10px;
}
</style>
