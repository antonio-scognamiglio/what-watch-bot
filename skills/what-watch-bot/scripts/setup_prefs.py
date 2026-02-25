import os
import sys
import argparse
import json

# Add project root to path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_connection, get_prefs

def main():
    parser = argparse.ArgumentParser(description="Setup user preferences")
    parser.add_argument("--set-genres", type=str, help="Comma-separated list of genre IDs")
    parser.add_argument("--set-platforms", type=str, help="Comma-separated list of platform IDs")
    parser.add_argument("--set-include-watched", type=str, help="Set include_watched preference (true/false)")
    parser.add_argument("--set-min-year", type=str, help="Set minimum release year (e.g., 2010), or pass 'none' to clear")
    parser.add_argument("--set-max-results", type=str, help="Set max items per search page (integer between 1 and 20)")
    parser.add_argument("--set-language", type=str, help="Set language preference (e.g., en-US, it-IT, fr-FR)")
    parser.add_argument("--set-region", type=str, help="Set streaming region (e.g., US, IT, FR)")
    parser.add_argument("--set-min-score", type=str, help="Set minimum Rotten Tomatoes score (0-100)")
    parser.add_argument("--view", action="store_true", help="View current preferences")
    args = parser.parse_args()

    conn = get_connection()
    cursor = conn.cursor()

    if args.set_genres:
        genre_list = [int(x.strip()) for x in args.set_genres.split(',') if x.strip()]
        cursor.execute(
            "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
            ('genres', json.dumps(genre_list))
        )
        conn.commit()
        print(json.dumps({"success": True, "message": "Genres updated", "genres": genre_list}))

    if args.set_platforms:
        platform_list = [int(x.strip()) for x in args.set_platforms.split(',') if x.strip()]
        cursor.execute(
            "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
            ('platforms', json.dumps(platform_list))
        )
        conn.commit()
        print(json.dumps({"success": True, "message": "Platforms updated", "platforms": platform_list}))

    if args.set_include_watched is not None:
        val_bool = args.set_include_watched.lower() in ('true', '1', 'yes')
        cursor.execute(
            "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
            ('include_watched', json.dumps(val_bool))
        )
        conn.commit()
        print(json.dumps({"success": True, "message": "include_watched updated", "include_watched": val_bool}))

    if args.set_min_year is not None:
        if args.set_min_year.lower() == 'none':
            cursor.execute("DELETE FROM prefs WHERE key = ?", ('min_year',))
            conn.commit()
            print(json.dumps({"success": True, "message": "min_year cleared"}))
        else:
            try:
                year = int(args.set_min_year)
                cursor.execute(
                    "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
                    ('min_year', json.dumps(year))
                )
                conn.commit()
                print(json.dumps({"success": True, "message": "min_year updated", "min_year": year}))
            except ValueError:
                print(json.dumps({"success": False, "error": "Invalid min_year format. Must be integer or 'none'."}))

    if args.set_max_results is not None:
        try:
            max_res = int(args.set_max_results)
            if 1 <= max_res <= 20:
                cursor.execute(
                    "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
                    ('max_results', json.dumps(max_res))
                )
                conn.commit()
                print(json.dumps({"success": True, "message": "max_results updated", "max_results": max_res}))
            else:
                print(json.dumps({"success": False, "error": "max_results must be between 1 and 20."}))
        except ValueError:
            print(json.dumps({"success": False, "error": "Invalid max_results format. Must be an integer."}))

    if args.set_language is not None:
        cursor.execute(
            "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
            ('language', json.dumps(args.set_language))
        )
        conn.commit()
        print(json.dumps({"success": True, "message": "Language updated", "language": args.set_language}))

    if args.set_region is not None:
        region = args.set_region.upper()
        cursor.execute(
            "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
            ('region', json.dumps(region))
        )
        conn.commit()
        print(json.dumps({"success": True, "message": "Region updated", "region": region}))

    if args.set_min_score is not None:
        try:
            score = int(args.set_min_score)
            if 0 <= score <= 100:
                cursor.execute(
                    "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
                    ('rt_min_score', json.dumps(score))
                )
                conn.commit()
                print(json.dumps({"success": True, "message": "rt_min_score updated", "rt_min_score": score}))
            else:
                print(json.dumps({"success": False, "error": "rt_min_score must be between 0 and 100."}))
        except ValueError:
            print(json.dumps({"success": False, "error": "Invalid rt_min_score format. Must be an integer."}))

    no_set_args = (
        not args.set_genres and not args.set_platforms and
        args.set_include_watched is None and args.set_min_year is None and
        args.set_max_results is None and args.set_language is None and
        args.set_region is None and args.set_min_score is None
    )
    if args.view or no_set_args:
        prefs = get_prefs(conn)
        # Apply defaults for display if keys are missing
        prefs.setdefault('language', 'en-US')
        prefs.setdefault('region', 'US')
        prefs.setdefault('rt_min_score', 70)
        print(json.dumps(prefs, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
