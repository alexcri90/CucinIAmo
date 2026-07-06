// ═══════════════════════════════════════════════════════════════
// 📖 RECIPE DETAILS - Dettaglio ricetta espandibile
// Usato sia nelle card del menù generato sia nel ricettario.
// ═══════════════════════════════════════════════════════════════

import type { Dish } from '../types';

const RecipeDetails = ({ dish }: { dish: Dish }) => (
  <details className="recipe-details">
    <summary>📖 Vedi Ricetta</summary>
    <div className="recipe-content">
      <h5>Ingredienti:</h5>
      <ul>
        {dish.recipe.ingredients.map((ing, i) => (
          <li key={i}>{ing.quantity} {ing.name}</li>
        ))}
      </ul>
      <h5>Procedimento:</h5>
      <ol>
        {dish.recipe.steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
      {dish.recipe.chef_notes && (
        <>
          <h5>💡 Note dello Chef:</h5>
          <p>{dish.recipe.chef_notes}</p>
        </>
      )}
      {dish.recipe.prep_ahead_timing && (
        <p><strong>⏰ Preparazione anticipata:</strong> {dish.recipe.prep_ahead_timing}</p>
      )}
    </div>
  </details>
);

export default RecipeDetails;
