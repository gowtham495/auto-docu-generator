import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Auto-Documentation Generator")
    parser.add_argument("--record", action="store_true", help="Start recording inputs")
    parser.add_argument("--generate", action="store_true", help="Generate documentation from last session")
    
    args = parser.parse_args()

    if args.record:
        from recorder import Recorder
        recorder = Recorder()
        try:
            recorder.start_recording()
        except KeyboardInterrupt:
            recorder.stop_recording()
    
    elif args.generate:
        from generator import Generator
        generator = Generator()
        generator.generate_report()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
