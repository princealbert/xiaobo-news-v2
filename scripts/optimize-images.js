#!/usr/bin/env node
import sharp from 'sharp'
import { glob } from 'glob'

async function optimizeImage(inputPath) {
  const outputPath = inputPath.replace(/\.(jpg|jpeg|png)$/, '.webp')
  try {
    await sharp(inputPath).webp({ quality: 85 }).toFile(outputPath)
    console.log(`✅ ${inputPath} → ${outputPath}`)
    return true
  } catch (error) {
    console.error(`❌ ${inputPath}: ${error.message}`)
    return false
  }
}

async function main() {
  console.log('🚀 优化图片...\n')
  const images = await glob('public/**/*.{jpg,jpeg,png}')
  console.log(`找到 ${images.length} 张图片\n`)
  
  let count = 0
  for (const img of images) {
    if (await optimizeImage(img)) count++
  }
  
  console.log(`\n✅ 完成：${count}/${images.length}`)
}

main().catch(console.error)
