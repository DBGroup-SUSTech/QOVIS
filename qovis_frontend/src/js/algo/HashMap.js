export class HashMap {
  constructor(hashFn, equalsFn) {
    this.buckets = {};
    this.size = 0;
    this.hashFn = hashFn || this.defaultHashFn;
    this.equalsFn = equalsFn || this.defaultEqualsFn;
  }

  set(key, value) {
    const hash = this.hashFn(key);
    const bucket = this.buckets[hash] || [];

    for (let i = 0; i < bucket.length; i++) {
      const entry = bucket[i];
      if (this.equalsFn(entry.key, key)) {
        entry.value = value;
        return;
      }
    }

    bucket.push({ key, value });
    this.size += 1;
    this.buckets[hash] = bucket;
  }

  get(key) {
    const hash = this.hashFn(key);
    const bucket = this.buckets[hash] || [];

    for (let i = 0; i < bucket.length; i++) {
      const entry = bucket[i];
      if (this.equalsFn(entry.key, key)) {
        return entry.value;
      }
    }

    return null;
  }

  remove(key) {
    const hash = this.hashFn(key);
    const bucket = this.buckets[hash] || [];

    for (let i = 0; i < bucket.length; i++) {
      const entry = bucket[i];
      if (this.equalsFn(entry.key, key)) {
        bucket.splice(i, 1);
        this.size -= 1;
        if (bucket.length === 0) {
          delete this.buckets[hash];
        }
        return;
      }
    }
  }

  has(key) {
    const hash = this.hashFn(key);
    const bucket = this.buckets[hash] || [];
    for (let i = 0; i < bucket.length; i++) {
      const entry = bucket[i];
      if (this.equalsFn(entry.key, key)) {
        return true;
      }
    }

    return false;
  }

  defaultHashFn(key) {
    if (typeof key === "string") {
      return key;
    } else {
      return key.toString();
    }
  }

  defaultEqualsFn(a, b) {
    return a === b;
  }
}
