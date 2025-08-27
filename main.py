"""Simple Document Classification Framework - Main Entry Point"""
import os
import sys
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description="Document Classification Framework")
    parser.add_argument("--file", "-f", help="Process single document file")
    parser.add_argument("--batch", "-b", help="Process all documents in directory") 
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    print("Document Classification Framework")
    print("=" * 50)
    
    # Check if Google API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.getenv("GOOGLE_API_KEY"):
            print("Error: GOOGLE_API_KEY not found in environment")
            print("Please check your .env file")
            return
    
    # Import the main framework
    try:
        from simple_framework import DocumentClassificationFramework
        framework = DocumentClassificationFramework()
        
        if args.file:
            print(f"Processing single document: {args.file}")
            result = framework.process_document(args.file)
            print("Processing completed!")
            print(f"Results: {result}")
            
        elif args.batch:
            print(f"Processing directory: {args.batch}")
            result = framework.process_directory(args.batch)
            print("Batch processing completed!")
            print(f"Results: {result}")
            
        else:
            # Interactive mode
            print("Interactive Mode")
            while True:
                print("\nOptions:")
                print("1. Process single document")
                print("2. Process directory")
                print("3. Exit")
                
                choice = input("Select option (1-3): ").strip()
                
                if choice == '1':
                    file_path = input("Enter document path: ").strip()
                    if file_path:
                        result = framework.process_document(file_path)
                        print(f"Results: {result}")
                
                elif choice == '2':
                    dir_path = input("Enter directory path: ").strip()
                    if dir_path:
                        result = framework.process_directory(dir_path)
                        print(f"Results: {result}")
                
                elif choice == '3':
                    print("Goodbye!")
                    break
                
                else:
                    print("Invalid option")
                    
    except ImportError as e:
        print(f"Error importing framework: {e}")
        print("Make sure all dependencies are installed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()