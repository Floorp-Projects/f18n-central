#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <f18n-root> <floorp-root> <translation-targets.json>" >&2
  exit 2
fi

F18N_ROOT="$(cd "$1" && pwd)"
FLOORP_ROOT="$(cd "$2" && pwd)"
MANIFEST_DIRECTORY="$(cd "$(dirname "$3")" && pwd)"
MANIFEST_PATH="$MANIFEST_DIRECTORY/$(basename "$3")"
TARGETS="$(cat "$MANIFEST_PATH")"

resolve_within() {
  local root="$1"
  local candidate="$2"
  local resolved
  resolved="$(realpath -m "$candidate")"
  case "$resolved/" in
    "$root"/*)
      if [ "$resolved" = "$root" ]; then
        echo "Refusing to use repository root as a synchronization target." >&2
        return 1
      fi
      printf '%s\n' "$resolved"
      ;;
    *)
      echo "Refusing to use path outside repository: $candidate" >&2
      return 1
      ;;
  esac
}

cd "$F18N_ROOT"
shopt -s nullglob
while read -r target; do
  TYPE="$(jq -r '.type // "file"' <<< "$target")"
  SOURCE_PATH="$(jq -r '.source_path' <<< "$target")"
  F18N_PATH="$(jq -r '.f18n_path' <<< "$target")"
  F18N_PATH="$(resolve_within "$F18N_ROOT" "$F18N_ROOT/$F18N_PATH")/"

  if [ "$TYPE" = "directory" ]; then
    SOURCE_LOCALE="$(jq -r '.source_locale' <<< "$target")"
    for LOCALE_DIR in "$F18N_PATH"*/; do
      [ -d "$LOCALE_DIR" ] || continue
      LOCALE="$(basename "$LOCALE_DIR")"
      if [ "$LOCALE" = "$SOURCE_LOCALE" ]; then
        continue
      fi

      DEST_DIR="$(
        resolve_within "$FLOORP_ROOT" "$FLOORP_ROOT/$SOURCE_PATH/$LOCALE"
      )"

      echo "Copying $LOCALE_DIR to $DEST_DIR"
      rm -rf "$DEST_DIR"
      mkdir -p "$DEST_DIR"
      cp -a "$LOCALE_DIR/." "$DEST_DIR/"
    done
  elif [ "$TYPE" = "file" ]; then
    SOURCE_FILE="$(jq -r '.source_file' <<< "$target")"
    DESTINATION_ROOT="$(
      resolve_within "$FLOORP_ROOT" "$FLOORP_ROOT/$SOURCE_PATH"
    )"
    mkdir -p "$DESTINATION_ROOT"
    for LOCALE_FILE in "$F18N_PATH"*.json; do
      if [ "$LOCALE_FILE" = "$F18N_PATH$SOURCE_FILE" ]; then
        continue
      fi
      LOCALE="$(basename "$LOCALE_FILE" .json)"
      echo "Copying $LOCALE_FILE to $DESTINATION_ROOT/$LOCALE.json"
      cp "$LOCALE_FILE" "$DESTINATION_ROOT/$LOCALE.json"
    done
  else
    echo "Unsupported translation target type: $TYPE" >&2
    exit 1
  fi
done < <(jq -c '.targets[]' <<< "$TARGETS")
shopt -u nullglob
