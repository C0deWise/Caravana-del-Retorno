## Descripción del Cambio
## ID de la Historia de Usuario
- **HU:** [Ej: 1GU-1]

## Checklist de Autorevisión (Antes de asignar a QA)
- [ ] ¿El código sigue el estándar **PEP 8 / ESLint/Prettier**?
- [ ] ¿La nomenclatura es correcta (**snake_case** en Back(ES) / **camelCase** en Front(EN))?
- [ ] ¿Los modelos y esquemas están dentro de su **módulo correspondiente**?
- [ ] ¿Se incluyeron **pruebas unitarias** con cobertura mínima del 70%?
- [ ] ¿Las validaciones de negocio (Documento > 0, Celular 10 dígitos, etc.) están implementadas?

## ¿Cómo probar este cambio?
**Backend:**
1. Levantar con Docker.
2. Probar en Swagger (`/docs`) con estos datos: `{...}`

**Frontend:**
1. Ir a la ruta: `localhost:3000/...`
2. Acción: (Ej: Hacer clic en el botón de registro).

## Capturas de Pantalla / Logs (Opcional)