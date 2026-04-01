declare module 'react-dom/client' {
  import { Container } from 'react-dom'
  
  interface Root {
    render(children: React.ReactNode): void
    unmount(): void
  }
  
  function createRoot(
    container: Container,
    options?: {
      onRecoverableError?: (error: unknown) => void
    }
  ): Root
  
  function hydrateRoot(
    container: Container,
    initialChildren: React.ReactNode,
    options?: {
      onRecoverableError?: (error: unknown) => void
    }
  ): Root
}
