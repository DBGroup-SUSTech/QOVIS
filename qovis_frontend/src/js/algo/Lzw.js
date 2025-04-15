import {HashMap} from "@/js/algo/HashMap"

export class LzwAlgo {
  /** @type {number[][]} */
  presets
  /** @type {number | null} */
  limit
  /** @type {HashMap} */
  dictionary
  /** @type {Map<number, number[]>} */
  antiDictionary

  constructor(presets, limit=null) {
    this.presets = presets ?? []
    this.limit = limit
  }

  createNewDictionary() {
    return new HashMap(LzwAlgo.hash, LzwAlgo.equals)
  }

  /**
   * @returns {Map<number, number[]>}
   */
  get parsedDictionary() {
    const ret = new Map()

    const buckets = this.dictionary.buckets
    Object.keys(buckets).forEach(k => {
      const list = buckets[k]
      list.forEach(({key, value}) => ret.set(value, key))
    })

    return ret
  }

  /**
   * @param {number[]} a
   * @param {number[]} b
   */
  static equals(a, b) {
    if (a.length !== b.length) {
      return false
    }
    for (let i = 0; i < a.length; i++) {
      if (a[i] !== b[i]) {
        return false
      }
    }
    return true
  }

  /**
   * @param {number[]} a
   */
  static hash(a) {
    return a.join('')
  }

  /**
   * Compress a list of indices to an array of compressed indices
   * @param {number[]} uncompressed
   * @returns {number[]}
   */
  compress(uncompressed) {
    const dictionary = this.dictionary = this.createNewDictionary()
    this.presets.forEach((preset, i) => dictionary.set(preset, i))

    let nextCode = dictionary.size
    const compressed = []
    let prefix = []

    for (let i = 0; i < uncompressed.length; i++) {
      const character = uncompressed[i]
      const stringPlusCharacter = prefix.concat([character])

      if (dictionary.has(stringPlusCharacter)) {
        prefix = stringPlusCharacter
      } else {
        // output the code for prefix
        compressed.push(dictionary.get(prefix))
        // add stringPlusCharacter to the dictionary
        dictionary.set(stringPlusCharacter, nextCode)
        nextCode++
        // update prefix
        prefix = [character]
      }
    }

    if (prefix.length > 0) {
      compressed.push(dictionary.get(prefix))
    }

    // compressed.push(LzwAlgo.END_FLAG)

    return compressed
  }

  /**
   * @param {number[]} compressed
   * @returns {number[]}
   */
  decompress(compressed) {
    if (compressed.length === 0) {
      return []
    }

    // this dictionary is different. It maps code to original "string" (number list).
    /** @type {Map<number, number[]>} */
    const dictionary = this.antiDictionary = new Map()
    this.presets.forEach((preset, i) => dictionary.set(i, preset))

    let nextCode = dictionary.size
    let previous
    let current = compressed[0]
    const decompressed = [...dictionary.get(current)]

    for (let i = 1; i < compressed.length; i++) {
      previous = current
      current = compressed[i]

      if (dictionary.has(current)) {
        // decode and output current word
        const currentStr = dictionary.get(current)
        decompressed.push(...currentStr)
        // update dictionary
        const p = dictionary.get(previous)
        const c = [currentStr[0]]
        dictionary.set(nextCode, p.concat(c))
        nextCode++
      } else {
        const p = dictionary.get(previous)
        const c = [p[0]]
        // update dictionary
        dictionary.set(nextCode, p.concat(c))
        nextCode++
        // output
        decompressed.push(...p.concat(c))
      }
    }

    return decompressed
  }
}
