import { SourceLocation } from "../../shared/meta";
import { ASTNode } from "../nodes/nodes";

function serializeClass<T>(obj: T): any {
    if (obj === null || typeof obj !== 'object') return obj;
  
    if (Array.isArray(obj)) {
        return obj.map(item => serializeClass(item));
    }
  
    // Special case: SourceLocation
    if (obj instanceof SourceLocation) {
        return `${obj.line}:${obj.column}:${obj.file}`;
    }
  
  
    const isClassInstance = obj.constructor && obj.constructor.name !== 'Object';
    const result: any = {};
  
    // Add className only if needed (skip for plain objects)
    if (isClassInstance) {
        result.className = obj.constructor.name;
    }
  
    for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
            result[key] = serializeClass((obj as any)[key]);
        }
    }
  
    return result;
  }
  
export function serialize<T>(obj: T): any {
    return JSON.stringify(serializeClass(obj), null, 2);
}