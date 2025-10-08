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

        <!-- Bulk Mode Toggle -->
        <div class="form-group">
          <div class="checkbox">
            <label>
              <input
                type="checkbox"
                v-model="bulkMode"
                :disabled="importing"
              />
              <strong>Bulk Import Mode</strong> (upload multiple PDF files at once)
            </label>
          </div>
        </div>

        <!-- File Upload -->
        <div class="form-group">
          <label for="file-upload">
            <span v-if="!bulkMode">PDF Statement</span>
            <span v-else>PDF Statements (Multiple Files)</span>
          </label>
          <input
            id="file-upload"
            type="file"
            accept=".pdf"
            @change="onFileChange"
            class="form-control"
            :disabled="!selectedBank || importing"
            :multiple="bulkMode"
            ref="fileInput"
          />
          <p class="help-block" v-if="!bulkMode">
            Maximum file size: 20MB per file. Only PDF files are accepted.
          </p>
          <p class="help-block" v-else>
            Maximum file size: 20MB per file. You can select multiple PDF files from the same bank.
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

        <!-- File Info - Single Mode -->
        <div v-if="file && !bulkMode" class="alert alert-info">
          <strong>Selected file:</strong> {{ file.name }}
          ({{ formatFileSize(file.size) }})
        </div>

        <!-- File Info - Bulk Mode -->
        <div v-if="files.length > 0 && bulkMode" class="alert alert-info">
          <strong>Selected files:</strong> {{ files.length }} PDF(s)
          <ul class="file-list">
            <li v-for="(f, index) in files" :key="index">
              {{ f.name }} ({{ formatFileSize(f.size) }})
            </li>
          </ul>
          <p><strong>Total size:</strong> {{ formatFileSize(totalFileSize) }}</p>
        </div>

        <!-- Progress - Single Mode -->
        <div v-if="importing && !bulkMode" class="progress">
          <div
            class="progress-bar progress-bar-striped active"
            role="progressbar"
            style="width: 100%"
          >
            <span>Processing statement...</span>
          </div>
        </div>

        <!-- Progress - Bulk Mode -->
        <div v-if="importing && bulkMode" class="bulk-progress">
          <div class="alert alert-info">
            <h4>
              <i class="fa fa-spinner fa-spin"></i>
              Processing {{ currentFileIndex }} of {{ files.length }} files...
            </h4>
            <p v-if="currentFileName">
              <strong>Current file:</strong> {{ currentFileName }}
            </p>
          </div>

          <div class="progress">
            <div
              class="progress-bar progress-bar-striped active"
              role="progressbar"
              :style="{ width: bulkProgressPercent + '%' }"
            >
              <span>{{ bulkProgressPercent }}%</span>
            </div>
          </div>

          <!-- Per-file results -->
          <div v-if="bulkResults.length > 0" class="bulk-results">
            <h5><i class="fa fa-files-o"></i> Completed Files:</h5>
            <table class="table table-condensed table-striped table-bordered">
              <thead>
                <tr class="active">
                  <th>File</th>
                  <th class="text-center">Status</th>
                  <th class="text-center" title="Total transactions found in PDF">
                    <i class="fa fa-list"></i> Total
                  </th>
                  <th class="text-center" title="Transactions successfully imported">
                    <i class="fa fa-plus-circle text-success"></i> Created
                  </th>
                  <th class="text-center" title="Duplicate transactions skipped">
                    <i class="fa fa-clone text-warning"></i> Duplicates
                  </th>
                  <th class="text-center" title="Transfer transactions detected">
                    <i class="fa fa-exchange text-info"></i> Transfers
                  </th>
                  <th class="text-center" title="Errors encountered">
                    <i class="fa fa-exclamation-circle text-danger"></i> Errors
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(result, index) in bulkResults" :key="index" :class="result.success ? '' : 'danger'">
                  <td>
                    <i class="fa fa-file-pdf-o"></i>
                    <strong>{{ result.filename }}</strong>
                  </td>
                  <td class="text-center">
                    <i class="fa" :class="result.success ? 'fa-check-circle text-success' : 'fa-times-circle text-danger'"></i>
                    <strong>{{ result.success ? 'Success' : 'Failed' }}</strong>
                  </td>
                  <td class="text-center">
                    <span class="badge badge-default">{{ result.data ? result.data.total : 0 }}</span>
                  </td>
                  <td class="text-center">
                    <span class="badge badge-success">{{ result.data ? result.data.created : 0 }}</span>
                  </td>
                  <td class="text-center">
                    <span class="badge badge-warning">{{ result.data ? result.data.duplicates : 0 }}</span>
                  </td>
                  <td class="text-center">
                    <span class="badge badge-info">{{ result.data ? (result.data.transfers || 0) : 0 }}</span>
                  </td>
                  <td class="text-center">
                    <span class="badge" :class="result.data && result.data.errors > 0 ? 'badge-danger' : 'badge-default'">
                      {{ result.data ? (result.data.errors || 0) : (result.success ? 0 : 1) }}
                    </span>
                  </td>
                </tr>
              </tbody>
              <tfoot v-if="bulkResults.length > 1">
                <tr class="info">
                  <td><strong>TOTALS</strong></td>
                  <td class="text-center">
                    <strong>{{ bulkSummary.successCount }}/{{ bulkSummary.totalFiles }}</strong>
                  </td>
                  <td class="text-center">
                    <span class="badge badge-default"><strong>{{ bulkSummary.totalTransactions }}</strong></span>
                  </td>
                  <td class="text-center">
                    <span class="badge badge-success"><strong>{{ bulkSummary.totalCreated }}</strong></span>
                  </td>
                  <td class="text-center">
                    <span class="badge badge-warning"><strong>{{ bulkSummary.totalDuplicates }}</strong></span>
                  </td>
                  <td class="text-center">
                    <span class="badge badge-info"><strong>{{ bulkSummary.totalTransfers }}</strong></span>
                  </td>
                  <td class="text-center">
                    <span class="badge" :class="bulkSummary.failedCount > 0 ? 'badge-danger' : 'badge-default'">
                      <strong>{{ bulkSummary.failedCount }}</strong>
                    </span>
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- Results - Single Mode -->
        <div v-if="importResult && !bulkMode" class="alert" :class="resultAlertClass">
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

        <!-- Results - Bulk Mode Summary -->
        <div v-if="bulkComplete && bulkMode" class="alert alert-success" style="margin-top: 20px; border: 2px solid #3c763d;">
          <h4 style="margin-top: 0;">
            <i class="fa fa-check-circle"></i>
            <strong>Bulk Import Complete!</strong>
          </h4>
          <hr style="margin: 15px 0; border-top: 1px solid #3c763d;">
          <div class="import-stats">
            <h5 style="margin-top: 0; margin-bottom: 15px;"><i class="fa fa-bar-chart"></i> Import Summary</h5>
            <table class="table table-condensed table-bordered" style="background-color: white;">
              <thead>
                <tr style="background-color: #dff0d8;">
                  <th colspan="2" class="text-center"><strong>FILES</strong></th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Total files processed:</strong></td>
                  <td class="text-right"><strong>{{ bulkSummary.filesProcessed }} / {{ bulkSummary.totalFiles }}</strong></td>
                </tr>
                <tr class="success">
                  <td><i class="fa fa-check-circle"></i> <strong>Successful imports:</strong></td>
                  <td class="text-right"><strong>{{ bulkSummary.successCount }}</strong></td>
                </tr>
                <tr v-if="bulkSummary.failedCount > 0" class="danger">
                  <td><i class="fa fa-times-circle"></i> <strong>Failed imports:</strong></td>
                  <td class="text-right"><strong>{{ bulkSummary.failedCount }}</strong></td>
                </tr>
              </tbody>
              <thead>
                <tr style="background-color: #dff0d8;">
                  <th colspan="2" class="text-center"><strong>TRANSACTIONS</strong></th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><i class="fa fa-list"></i> <strong>Total transactions found:</strong></td>
                  <td class="text-right"><strong>{{ bulkSummary.totalTransactions }}</strong></td>
                </tr>
                <tr class="success">
                  <td><i class="fa fa-plus-circle"></i> <strong>Transactions imported:</strong></td>
                  <td class="text-right"><strong style="font-size: 16px; color: #3c763d;">{{ bulkSummary.totalCreated }}</strong></td>
                </tr>
                <tr class="warning">
                  <td><i class="fa fa-clone"></i> <strong>Duplicates skipped:</strong></td>
                  <td class="text-right"><strong>{{ bulkSummary.totalDuplicates }}</strong></td>
                </tr>
                <tr v-if="bulkSummary.totalTransfers > 0" class="info">
                  <td><i class="fa fa-exchange"></i> <strong>Transfers detected:</strong></td>
                  <td class="text-right"><strong>{{ bulkSummary.totalTransfers }}</strong></td>
                </tr>
                <tr v-if="bulkSummary.totalErrors > 0" class="danger">
                  <td><i class="fa fa-exclamation-circle"></i> <strong>Transaction errors:</strong></td>
                  <td class="text-right"><strong>{{ bulkSummary.totalErrors }}</strong></td>
                </tr>
              </tbody>
            </table>

            <!-- Error Details Section -->
            <div v-if="filesWithErrors.length > 0" class="error-summary" style="margin-top: 20px;">
              <h5 style="margin-top: 0; margin-bottom: 15px; color: #a94442;">
                <i class="fa fa-exclamation-triangle"></i> Files with Errors ({{ filesWithErrors.length }})
              </h5>
              <div class="panel-group" id="error-accordion">
                <div v-for="(fileError, index) in filesWithErrors" :key="index" class="panel panel-danger">
                  <div class="panel-heading">
                    <h4 class="panel-title">
                      <a data-toggle="collapse" :data-parent="'#error-accordion'" :href="'#error-' + index">
                        <i class="fa fa-file-pdf-o"></i>
                        <strong>{{ fileError.filename }}</strong>
                        <span class="badge badge-danger pull-right">{{ fileError.errorCount }} error(s)</span>
                      </a>
                    </h4>
                  </div>
                  <div :id="'error-' + index" class="panel-collapse collapse" :class="{ 'in': index === 0 }">
                    <div class="panel-body">
                      <p><strong>Status:</strong> {{ fileError.message }}</p>
                      <p v-if="fileError.data">
                        <strong>Transactions:</strong>
                        {{ fileError.data.created }} created,
                        {{ fileError.data.duplicates }} duplicates,
                        <span class="text-danger">{{ fileError.data.errors }} errors</span>
                      </p>
                      <div v-if="fileError.debug_error" class="error-log">
                        <strong>Error Log:</strong>
                        <pre style="max-height: 200px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 11px;">{{ fileError.debug_error }}</pre>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
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
          <li><strong>Commonwealth Bank (Credit Card):</strong> Credit card statements</li>
          <li><strong>Commonwealth Bank (Home Loan):</strong> Home loan statements</li>
          <li><strong>Commonwealth Bank (Everyday Offset):</strong> Everyday Offset account statements</li>
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
      files: [],
      bulkMode: false,
      detectDuplicates: true,
      detectTransfers: true,
      importing: false,
      importResult: null,
      errorMessage: null,
      // Bulk mode data
      currentFileIndex: 0,
      currentFileName: '',
      bulkResults: [],
      bulkComplete: false,
      bulkSummary: {
        totalFiles: 0,
        filesProcessed: 0,
        successCount: 0,
        failedCount: 0,
        totalTransactions: 0,
        totalCreated: 0,
        totalDuplicates: 0,
        totalTransfers: 0,
        totalErrors: 0
      }
    };
  },

  computed: {
    selectedBankInfo() {
      return this.banks.find(b => b.value === this.selectedBank);
    },

    canUpload() {
      if (this.bulkMode) {
        return this.selectedBank && this.files.length > 0 && !this.importing;
      }
      return this.selectedBank && this.file && !this.importing;
    },

    totalFileSize() {
      return this.files.reduce((sum, f) => sum + f.size, 0);
    },

    bulkProgressPercent() {
      if (this.bulkSummary.totalFiles === 0) return 0;
      return Math.round((this.bulkSummary.filesProcessed / this.bulkSummary.totalFiles) * 100);
    },

    resultAlertClass() {
      if (!this.importResult) return '';
      return this.importResult.success ? 'alert-success' : 'alert-danger';
    },

    resultIconClass() {
      if (!this.importResult) return '';
      return this.importResult.success ? 'fa-check-circle' : 'fa-exclamation-circle';
    },

    filesWithErrors() {
      // Return array of files that had errors during import
      return this.bulkResults.filter(result => {
        // Include files that completely failed OR had transaction errors
        if (!result.success) {
          return true;
        }
        if (result.data && result.data.errors > 0) {
          return true;
        }
        return false;
      }).map(result => {
        // Calculate error count
        let errorCount = 0;
        if (!result.success) {
          errorCount = result.data ? (result.data.total || 0) : 1;
        } else if (result.data) {
          errorCount = result.data.errors || 0;
        }

        return {
          filename: result.filename,
          message: result.message,
          data: result.data,
          debug_error: result.debug_error,
          errorCount: errorCount
        };
      });
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
      this.errorMessage = null;
      this.importResult = null;
      this.bulkResults = [];
      this.bulkComplete = false;

      if (this.bulkMode) {
        // Handle multiple files
        const selectedFiles = Array.from(event.target.files);

        // Validate all files
        const validFiles = [];
        for (const file of selectedFiles) {
          if (file.type !== 'application/pdf') {
            this.errorMessage = `File "${file.name}" is not a PDF`;
            this.$refs.fileInput.value = '';
            return;
          }
          if (file.size > 20 * 1024 * 1024) {
            this.errorMessage = `File "${file.name}" exceeds 20MB limit`;
            this.$refs.fileInput.value = '';
            return;
          }
          validFiles.push(file);
        }

        this.files = validFiles;
        this.file = null;
      } else {
        // Handle single file
        const file = event.target.files[0];
        if (file) {
          // Validate file type
          if (file.type !== 'application/pdf') {
            this.errorMessage = 'Please select a PDF file';
            this.$refs.fileInput.value = '';
            return;
          }

          // Validate file size (20MB)
          if (file.size > 20 * 1024 * 1024) {
            this.errorMessage = 'File size must be less than 20MB';
            this.$refs.fileInput.value = '';
            return;
          }

          this.file = file;
          this.files = [];
        }
      }
    },

    async uploadStatement() {
      if (!this.canUpload) return;

      if (this.bulkMode) {
        await this.uploadBulk();
      } else {
        await this.uploadSingle();
      }
    },

    async uploadSingle() {
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

    async uploadBulk() {
      this.importing = true;
      this.importResult = null;
      this.errorMessage = null;
      this.bulkResults = [];
      this.bulkComplete = false;

      // Initialize summary
      this.bulkSummary = {
        totalFiles: this.files.length,
        filesProcessed: 0,
        successCount: 0,
        failedCount: 0,
        totalTransactions: 0,
        totalCreated: 0,
        totalDuplicates: 0,
        totalTransfers: 0,
        totalErrors: 0
      };

      // Process files sequentially
      for (let i = 0; i < this.files.length; i++) {
        this.currentFileIndex = i + 1;
        this.currentFileName = this.files[i].name;

        const formData = new FormData();
        formData.append('file', this.files[i]);
        formData.append('bank_type', this.selectedBank);
        formData.append('detect_duplicates', this.detectDuplicates ? '1' : '0');
        formData.append('detect_transfers', this.detectTransfers ? '1' : '0');

        try {
          const response = await axios.post('/api/v1/statement-import/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });

          // Add result to bulk results
          this.bulkResults.push({
            filename: this.files[i].name,
            success: response.data.success,
            message: response.data.message,
            data: response.data.data,
            debug_error: response.data.debug_error || ''
          });

          // Update summary
          this.bulkSummary.filesProcessed++;
          if (response.data.success) {
            this.bulkSummary.successCount++;
            if (response.data.data) {
              this.bulkSummary.totalTransactions += response.data.data.total || 0;
              this.bulkSummary.totalCreated += response.data.data.created || 0;
              this.bulkSummary.totalDuplicates += response.data.data.duplicates || 0;
              this.bulkSummary.totalTransfers += response.data.data.transfers || 0;
              this.bulkSummary.totalErrors += response.data.data.errors || 0;
            }
          } else {
            this.bulkSummary.failedCount++;
          }

        } catch (error) {
          console.error(`Upload error for ${this.files[i].name}:`, error);

          // Add error result
          this.bulkResults.push({
            filename: this.files[i].name,
            success: false,
            message: error.response?.data?.message || 'Upload failed',
            data: error.response?.data?.data || null,
            debug_error: error.response?.data?.debug_error || error.message
          });

          this.bulkSummary.filesProcessed++;
          this.bulkSummary.failedCount++;

          // Count errors from failed file if available
          if (error.response?.data?.data?.errors) {
            this.bulkSummary.totalErrors += error.response.data.data.errors;
          }
        }
      }

      // Mark bulk import as complete
      this.bulkComplete = true;
      this.importing = false;
      this.currentFileName = '';
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
      this.files = [];
      this.importResult = null;
      this.errorMessage = null;
      this.detectDuplicates = true;
      this.detectTransfers = true;
      this.bulkResults = [];
      this.bulkComplete = false;
      this.currentFileIndex = 0;
      this.currentFileName = '';
      this.bulkSummary = {
        totalFiles: 0,
        filesProcessed: 0,
        successCount: 0,
        failedCount: 0,
        totalTransactions: 0,
        totalCreated: 0,
        totalDuplicates: 0,
        totalTransfers: 0
      };
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

/* Bulk upload styles */
.file-list {
  max-height: 200px;
  overflow-y: auto;
  margin: 10px 0;
  padding-left: 20px;
}

.file-list li {
  margin-bottom: 5px;
}

.bulk-progress {
  margin-top: 20px;
}

.bulk-results {
  margin-top: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.bulk-results table {
  font-size: 13px;
}

.bulk-results th {
  position: sticky;
  top: 0;
  background: #f5f5f5;
  z-index: 10;
}
</style>
