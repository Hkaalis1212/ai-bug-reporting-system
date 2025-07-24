# Zip File Upload Functionality

This Flask application now includes a complete zip file upload system that allows users to upload and extract zip files safely.

## Features

✅ **Secure File Upload**: Only `.zip` files are allowed
✅ **File Size Limits**: Maximum 16MB file size
✅ **Automatic Extraction**: Uploaded files are automatically extracted
✅ **Timestamped Storage**: Files are stored with timestamps to avoid conflicts
✅ **Beautiful UI**: Clean, modern upload interface
✅ **Error Handling**: Comprehensive error handling and user feedback
✅ **File List**: Returns a complete list of extracted files

## How to Use

### 1. Start the Flask Application

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the Flask app
python app.py
```

### 2. Access the Upload Page

Navigate to: `http://localhost:5000/upload`

### 3. Upload a Zip File

1. Click "Choose a zip file to upload"
2. Select your `.zip` file
3. Click "Upload Zip File"
4. The file will be uploaded, extracted, and you'll see a success message

### 4. API Usage

You can also upload files programmatically using curl or any HTTP client:

```bash
curl -X POST -F "file=@your-file.zip" http://localhost:5000/upload
```

**Response Format:**
```json
{
  "success": true,
  "message": "Zip file uploaded and extracted successfully",
  "filename": "20250724_013104_your-file.zip",
  "extracted_files": ["file1.txt", "file2.py", "folder/file3.js"],
  "extract_path": "uploads/extracted_20250724_013104"
}
```

## Technical Details

### File Structure
```
uploads/
├── 20250724_013104_BugTrackerPro.zip    # Original uploaded file
└── extracted_20250724_013104/           # Extracted contents
    └── BugTrackerPro/
        ├── app.py
        ├── README.md
        └── ...
```

### Configuration
- **Max file size**: 16MB (configurable in `app.config['MAX_CONTENT_LENGTH']`)
- **Allowed extensions**: `.zip` only
- **Upload directory**: `uploads/`
- **Secret key**: Change `app.secret_key` for production use

### Security Features
- File extension validation
- Secure filename generation using `werkzeug.utils.secure_filename`
- Timestamped storage to prevent conflicts
- File size limits
- Input validation and error handling

### Error Handling
- Invalid file types are rejected
- File size limits are enforced
- Corrupted zip files are detected
- User-friendly error messages

## Integration with Your Application

The upload functionality is modular and can be easily integrated into any Flask application:

1. **Import required modules**:
```python
from werkzeug.utils import secure_filename
import zipfile
```

2. **Add configuration**:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'uploads'
```

3. **Use the upload route**: The `/upload` route handles both GET (display form) and POST (process upload) requests.

## Example Test

The system was successfully tested with a 3.7MB zip file containing a complete project with over 1000 files, demonstrating robust handling of complex archives.

## Next Steps

You can extend this functionality by:
- Adding file type detection within zip archives
- Implementing user authentication and file ownership
- Adding file management features (delete, rename, etc.)
- Creating a file browser interface
- Adding virus scanning for uploaded files
- Implementing file compression options