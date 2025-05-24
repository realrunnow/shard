interface SerializeOptions {
  indentSize?: number;
  indentChar?: string;
  ignoreKeys?: Set<string>;
  visited?: WeakMap<object, true>;
}

export function serializeIndented<T>(object: T, options: SerializeOptions = {}): string {
  const {
    indentSize = 2,
    indentChar = ' ',
    ignoreKeys = new Set(['start', 'end']),
    visited = new WeakMap(),
  } = options;

  const indent = (level: number): string => indentChar.repeat(indentSize * level);

  const serialize = (value: any, level: number = 0): string => {
    // Handle primitives
    if (value === null || typeof value !== 'object') {
      return `${value}`;
    }

    // Prevent infinite recursion
    if (visited.has(value)) {
      return '[Circular]';
    }

    visited.set(value, true);

    // Special case: Identifier or TypeIdentifier
    const className = value.constructor?.name;
    if (className === 'Identifier' || className === 'TypeIdentifier') {
      return `${className}(${value.name ?? 'unknown'})`;
    }

    // Custom serialization
    if (typeof value.toDebugString === 'function') {
      return value.toDebugString({ ...options, visited });
    }

    // Handle arrays
    if (Array.isArray(value)) {
      if (value.length === 0) return '[]';

      const lines: string[] = ['['];
      for (const item of value) {
        lines.push(`${indent(level + 1)}${serialize(item, level + 1)}`);
      }
      lines.push(`${indent(level)}]`);
      return lines.join('\n');
    }

    // Handle objects
    const lines: string[] = [`${className || 'Object'}:`];

    for (const key of Object.keys(value)) {
      if (ignoreKeys.has(key)) continue;

      const val = value[key];
      if (typeof val === 'function') continue;

      const line = `${indent(level + 1)}${key} = ${serialize(val, level + 1)}`;
      lines.push(line);
    }

    return lines.join('\n');
  };

  return serialize(object);
}